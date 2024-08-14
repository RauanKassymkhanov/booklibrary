from app.api.base_service import BaseService
from pydantic import TypeAdapter
from sqlalchemy import select, insert, update, delete
from app.models import AuthorModel
from app.api.authors.schemas import AuthorCreate, Author
from app.api.exceptions import NotFoundError


class AuthorService(BaseService):
    async def get_authors(self) -> list[Author]:
        query = select(AuthorModel)
        result = await self._execute_in_session(query)
        authors = result.scalars().all()
        return TypeAdapter(list[Author]).validate_python(authors)

    async def _get_author_or_raise(self, author_id: int) -> Author:
        query = select(AuthorModel).where(AuthorModel.id == author_id)
        result = await self._execute_in_session(query)
        author = result.scalar_one_or_none()
        if author is None:
            raise NotFoundError("Author", author_id)
        return Author.model_validate(author)

    async def create_author(self, new_author: AuthorCreate) -> Author:
        query = (
            insert(AuthorModel)
            .values(**new_author.model_dump())
            .returning(AuthorModel)
        )
        result = await self._execute_in_session(query)
        created_author = result.scalar_one()
        return Author.model_validate(created_author)

    async def get_author(self, author_id: int) -> Author:
        return await self._get_author_or_raise(author_id)

    async def delete_author(self, author_id: int) -> None:
        await self._get_author_or_raise(author_id)
        delete_query = delete(AuthorModel).where(AuthorModel.id == author_id)
        await self._execute_in_session(delete_query)

    async def update_author(self, author_id: int, updated_author: AuthorCreate) -> Author:
        await self._get_author_or_raise(author_id)
        update_query = (
            update(AuthorModel)
            .values(**updated_author.model_dump())
            .where(AuthorModel.id == author_id)
            .returning(AuthorModel)
        )
        result = await self._execute_in_session(update_query)
        updated_author = result.scalar_one()
        return Author.model_validate(updated_author)

