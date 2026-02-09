from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class ReportBase(SQLModel):
    title: str = Field(index=True)
    description: str
    category: str = Field(index=True)  # e.g., 'pothole', 'street_light', 'waste'
    status: str = Field(default="pending", index=True)  # pending, in-progress, resolved, closed
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Report(ReportBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    # Relationship back to User (needs to be defined in User model too)
    user: "User" = Relationship(back_populates="reports")


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    id: int
    user_id: int
