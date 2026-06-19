from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.points import PointTransaction, Reward, RewardExchange, TransactionType
from app.schemas import PointTransactionCreate, RewardCreate, RewardUpdate, Reward as RewardSchema, PointTransaction as PointTransactionSchema, RewardExchangeCreate, RewardExchange as RewardExchangeSchema
from app.services import (
    get_current_active_user,
    get_current_admin,
    add_user_points,
)

router = APIRouter(prefix="/points", tags=["points and rewards"])


@router.get("/my-transactions", response_model=List[PointTransactionSchema])
def read_my_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    transactions = db.query(PointTransaction).filter(
        PointTransaction.user_id == current_user.id,
    ).order_by(PointTransaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/rewards", response_model=List[RewardSchema])
def read_rewards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    rewards = db.query(Reward).filter(Reward.is_active == True).order_by(Reward.points_required.asc()).offset(skip).limit(limit).all()
    return rewards


@router.post("/rewards", response_model=RewardSchema, status_code=status.HTTP_201_CREATED)
def create_reward(
    reward_in: RewardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    db_reward = Reward(
        name=reward_in.name,
        description=reward_in.description,
        points_required=reward_in.points_required,
        stock=reward_in.stock,
        image_url=reward_in.image_url,
        is_active=reward_in.is_active if reward_in.is_active is not None else True,
    )
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward


@router.put("/rewards/{reward_id}", response_model=RewardSchema)
def update_reward(
    reward_id: int,
    reward_in: RewardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    db_reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not db_reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found",
        )
    for key, value in reward_in.model_dump(exclude_unset=True).items():
        setattr(db_reward, key, value)
    db.commit()
    db.refresh(db_reward)
    return db_reward


@router.delete("/rewards/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> None:
    db_reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not db_reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found",
        )
    db.delete(db_reward)
    db.commit()


@router.post("/exchange", response_model=RewardExchangeSchema, status_code=status.HTTP_201_CREATED)
def exchange_reward(
    exchange_in: RewardExchangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    reward = db.query(Reward).filter(Reward.id == exchange_in.reward_id).first()
    if not reward or not reward.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found or not available",
        )
    if current_user.total_points < reward.points_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points",
        )
    if reward.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reward out of stock",
        )
    exchange = RewardExchange(
        user_id=current_user.id,
        reward_id=exchange_in.reward_id,
        points_spent=reward.points_required,
    )
    db.add(exchange)
    add_user_points(db, current_user.id, -reward.points_required)
    reward.stock -= 1
    transaction = PointTransaction(
        user_id=current_user.id,
        type=TransactionType.EXCHANGE,
        points=-reward.points_required,
        description=f"兑换奖励: {reward.name}",
    )
    db.add(transaction)
    db.commit()
    db.refresh(exchange)
    return exchange


@router.get("/my-exchanges", response_model=List[RewardExchangeSchema])
def read_my_exchanges(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    exchanges = db.query(RewardExchange).filter(
        RewardExchange.user_id == current_user.id,
    ).order_by(RewardExchange.created_at.desc()).offset(skip).limit(limit).all()
    return exchanges


@router.post("/admin/add-points", response_model=PointTransactionSchema, status_code=status.HTTP_201_CREATED)
def admin_add_points(
    transaction_in: PointTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    if transaction_in.points <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Points must be positive",
        )
    transaction = PointTransaction(
        user_id=transaction_in.user_id,
        type=transaction_in.type if transaction_in.type else TransactionType.AWARD,
        points=transaction_in.points,
        description=transaction_in.description,
    )
    db.add(transaction)
    add_user_points(db, transaction_in.user_id, transaction_in.points)
    db.commit()
    db.refresh(transaction)
    return transaction
