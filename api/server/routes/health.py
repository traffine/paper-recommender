from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

router = APIRouter()


@router.get("/health", name="Health check API")
async def health() -> None:
    """Health check API

    FastAPI health check

    Args:

    Returns:
    """
    try:
        return Response(status_code=status.HTTP_200_OK)
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=e
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e
        ) from e
