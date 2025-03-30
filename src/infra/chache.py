from dogpile.cache import make_region
from sqlalchemy import event

from src.infra.models import Player


player_cache = make_region().configure(
    'dogpile.cache.memory',
    expiration_time=1800,
)


@event.listens_for(Player, 'after_insert')
@event.listens_for(Player, 'after_update')
@event.listens_for(Player, 'after_delete')
def invalidate_players_cache(mapper, connection, target):
    print("Invalidate players cache")
    player_cache.invalidate()


def invalidate_all():
    player_cache.invalidate()