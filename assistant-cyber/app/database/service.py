from app.database.models import Ratings, Queries
from app.database.base import BaseService


class FeedService(BaseService):
    model=Ratings

class QueryService(BaseService):
    model=Queries
