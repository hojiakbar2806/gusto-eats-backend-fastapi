from fastapi import HTTPException
from pydantic import BaseModel, ValidationError


class CustomBaseModel(BaseModel):
    @classmethod
    def validate(cls, values):
        try:
            return super().validate(values)
        except ValidationError as exc:
            formatted_error = cls.format_errors(exc)
            raise HTTPException(status_code=422, detail=formatted_error)

    @staticmethod
    def format_errors(exc: ValidationError) -> str:
        formatted_errors = []
        for error in exc.errors():
            field = error['loc'][-1]  # Maydon nomi
            message = error['msg']  # Xato xabari
            formatted_errors.append(f"{field.capitalize()}: {message}")

        # Xatoliklarni bitta satrga aylantirish
        return "; ".join(formatted_errors)
