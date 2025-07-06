from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from database import get_db, MovieModel
from schemas.movies import MovieListResponseSchema, MovieDetailResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
):
    result = await db.execute(select(MovieModel))
    movies = result.scalars().all()

    total_items = len(movies)
    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = ceil(total_items / per_page)
    if page > total_pages:
        raise HTTPException(status_code=404, detail="No movies found.")

    start = (page - 1) * per_page
    end = start + per_page
    paginated_movies = movies[start:end]

    base_url = request.url.path  # e.g. /movies/
    prev_page = f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page = f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None

    return {
        "movies": paginated_movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items,
    }


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_by_id(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")
    return movie
