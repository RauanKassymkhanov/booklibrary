from sqlalchemy import select, insert, update, delete
from app.api.base_service import BaseService
from app.models import GenreModel
from app.api.genres.schemas import GenreCreate, Genre
from app.api.exceptions import NotFoundError


class GenreService(BaseService):
    async def get_genres(self) -> list[Genre]:
        query = select(GenreModel)
        result = await self._session.execute(query)
        genres = result.scalars().all()
        return [Genre.model_validate(genre) for genre in genres]

    async def create_genre(self, new_genre: GenreCreate) -> Genre:
        query = insert(GenreModel).values(**new_genre.model_dump()).returning(GenreModel)
        result = await self._session.execute(query)
        created_genre = result.scalar_one()
        return Genre.model_validate(created_genre)

    async def get_genre(self, genre_id: int) -> Genre:
        return await self._get_genre_or_raise(genre_id)

    async def delete_genre(self, genre_id: int) -> None:
        await self._get_genre_or_raise(genre_id)
        delete_query = delete(GenreModel).where(GenreModel.id == genre_id)
        await self._session.execute(delete_query)

    async def update_genre(self, genre_id: int, updated_genre: GenreCreate) -> Genre:
        await self._get_genre_or_raise(genre_id)
        update_query = (
            update(GenreModel)
            .values(**updated_genre.model_dump())
            .where(GenreModel.id == genre_id)
            .returning(GenreModel)
        )
        result = await self._session.execute(update_query)
        updated_genre = result.scalar_one()
        return Genre.model_validate(updated_genre)

    async def _get_genre_or_raise(self, genre_id: int) -> Genre:
        query = select(GenreModel).where(GenreModel.id == genre_id)
        result = await self._session.execute(query)
        genre = result.scalar_one_or_none()
        if genre is None:
            raise NotFoundError("Genre", genre_id)
        return Genre.model_validate(genre)
