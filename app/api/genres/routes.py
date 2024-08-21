from fastapi import APIRouter, Depends, HTTPException, status
from app.api.exceptions import NotFoundError
from app.api.genres.schemas import Genre, GenreCreate
from app.api.genres.service import GenreService

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", response_model=list[Genre])
async def get_genres(service: GenreService = Depends()):
    return await service.get_genres()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Genre)
async def create_genres(new_genre: GenreCreate, service: GenreService = Depends()):
    return await service.create_genre(new_genre)


@router.get("/{genre_id}", response_model=Genre)
async def get_genre(genre_id: int, service: GenreService = Depends()):
    try:
        return await service.get_genre(genre_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int, service: GenreService = Depends()):
    try:
        await service.delete_genre(genre_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/{genre_id}", response_model=Genre)
async def update_genre(genre_id: int, updated_genre: GenreCreate, service: GenreService = Depends()):
    try:
        return await service.update_genre(genre_id, updated_genre)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
