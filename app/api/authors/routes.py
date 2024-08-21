from fastapi import APIRouter, Depends, HTTPException, status
from app.api.authors.schemas import Author, AuthorCreate
from app.api.authors.service import AuthorService
from app.api.exceptions import NotFoundError

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=list[Author])
async def get_authors(service: AuthorService = Depends()):
    return await service.get_authors()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Author)
async def create_author(new_author: AuthorCreate, service: AuthorService = Depends()):
    return await service.create_author(new_author)


@router.get("/{author_id}", response_model=Author)
async def get_author(author_id: int, service: AuthorService = Depends()):
    try:
        return await service.get_author(author_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(author_id: int, service: AuthorService = Depends()):
    try:
        await service.delete_author(author_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/{author_id}", response_model=Author)
async def update_author(author_id: int, updated_author: AuthorCreate, service: AuthorService = Depends()):
    try:
        return await service.update_author(author_id, updated_author)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
