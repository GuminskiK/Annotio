import uuid
from sqlmodel import SQLModel, Field


class QualityMetricBase(SQLModel):
    rejection_rate: float = Field(default=0.0)
    total_tasks_completed: int = Field(default=0)
    ranking_score: float = Field(default=0.0)


class QualityMetric(QualityMetricBase, table=True):
    user_id: uuid.UUID = Field(primary_key=True)


class QualityMetricCreate(QualityMetricBase):
    user_id: uuid.UUID


class QualityMetricRead(QualityMetricBase):
    user_id: uuid.UUID


class QualityMetricUpdate(SQLModel):
    rejection_rate: float | None = None
    total_tasks_completed: int | None = None
    ranking_score: float | None = None
