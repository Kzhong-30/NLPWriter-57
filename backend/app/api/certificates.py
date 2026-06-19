from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.certificate import Certificate
from app.models.checkin import CheckInStatus
from app.schemas import CertificateGenerate, Certificate as CertificateSchema, CertificateWithUser
from app.utils.pdf_generator import generate_certificate_pdf
from app.utils.certificate_generator import generate_certificate_number
from app.services import (
    get_current_active_user,
    get_current_organizer,
    get_activity,
    add_user_points,
)

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.post("/generate", response_model=CertificateSchema, status_code=status.HTTP_201_CREATED)
def generate_certificate(
    cert_in: CertificateGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    activity = get_activity(db, activity_id=cert_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    if activity.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    existing_cert = db.query(Certificate).filter(
        Certificate.user_id == cert_in.user_id,
        Certificate.activity_id == cert_in.activity_id,
    ).first()
    if existing_cert:
        return existing_cert
    from app.models.checkin import CheckIn
    checkin = db.query(CheckIn).filter(
        CheckIn.user_id == cert_in.user_id,
        CheckIn.activity_id == cert_in.activity_id,
        CheckIn.status == CheckInStatus.CHECKED_OUT,
    ).first()
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has not completed this activity",
        )
    certificate_number = generate_certificate_number(
        user_id=cert_in.user_id,
        activity_id=cert_in.activity_id,
    )
    db_certificate = Certificate(
        user_id=cert_in.user_id,
        activity_id=cert_in.activity_id,
        certificate_number=certificate_number,
        service_hours=checkin.service_hours or 0,
        issue_date=cert_in.issue_date,
    )
    db.add(db_certificate)
    add_user_points(db, cert_in.user_id, 50)
    db.commit()
    db.refresh(db_certificate)
    return db_certificate


@router.get("/my", response_model=List[CertificateWithUser])
def read_my_certificates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    certificates = db.query(Certificate).filter(
        Certificate.user_id == current_user.id,
    ).order_by(Certificate.created_at.desc()).offset(skip).limit(limit).all()
    return certificates


@router.get("/user/{user_id}", response_model=List[CertificateWithUser])
def read_user_certificates(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if current_user.id != user_id and current_user.role not in [UserRole.ORGANIZER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    certificates = db.query(Certificate).filter(
        Certificate.user_id == user_id,
    ).order_by(Certificate.created_at.desc()).offset(skip).limit(limit).all()
    return certificates


@router.get("/activity/{activity_id}", response_model=List[CertificateWithUser])
def read_activity_certificates(
    activity_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
) -> Any:
    activity = get_activity(db, activity_id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    if activity.organizer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    certificates = db.query(Certificate).filter(
        Certificate.activity_id == activity_id,
    ).order_by(Certificate.created_at.desc()).offset(skip).limit(limit).all()
    return certificates


@router.get("/{certificate_id}", response_model=CertificateWithUser)
def read_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found",
        )
    if certificate.user_id != current_user.id and current_user.role not in [UserRole.ORGANIZER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return certificate


@router.get("/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found",
        )
    if certificate.user_id != current_user.id and current_user.role not in [UserRole.ORGANIZER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    pdf_buffer = generate_certificate_pdf(
        certificate_number=certificate.certificate_number,
        user_name=certificate.user.full_name if certificate.user else "Unknown",
        activity_title=certificate.activity.title if certificate.activity else "Unknown",
        service_hours=certificate.service_hours,
        issue_date=certificate.issue_date,
    )
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{certificate.certificate_number}.pdf"
        },
    )


@router.get("/verify/{certificate_number}", response_model=CertificateWithUser)
def verify_certificate(
    certificate_number: str,
    db: Session = Depends(get_db),
) -> Any:
    certificate = db.query(Certificate).filter(Certificate.certificate_number == certificate_number).first()
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found or invalid",
        )
    return certificate
