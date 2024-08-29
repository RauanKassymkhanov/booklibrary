from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.api.books.schemas import BookCreate, FullBookInfo
from app.api.books.service import BookService
from app.api.exceptions import NotFoundError

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[FullBookInfo])
async def get_books(service: BookService = Depends()):
    return await service.get_books()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FullBookInfo)
async def create_book(new_book: BookCreate, background_tasks: BackgroundTasks, service: BookService = Depends()):
    try:
        book_created = await service.create_book(new_book, background_tasks)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    return book_created


@router.get("/{book_id}", response_model=FullBookInfo)
async def get_book(book_id: int, service: BookService = Depends()):
    try:
        book = await service.get_book(book_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookService = Depends()):
    try:
        await service.delete_book(book_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/{book_id}", response_model=FullBookInfo)
async def update_book(book_id: int, updated_book: BookCreate, service: BookService = Depends()):
    try:
        return await service.update_book(book_id, updated_book)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
