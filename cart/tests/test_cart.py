from uuid import UUID

import pytest
from oes.cart.cart import Cart, CartRegistration, CartRepo, CartService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def repo(session: AsyncSession):
    return CartRepo(session)


@pytest.fixture
def service(repo: CartRepo):
    return CartService(repo, b"\0" * 8, "0.1.0")


def test_hash():
    cart = Cart(
        event_id="test",
        meta={"meta": "meta"},
        registrations=[
            CartRegistration(
                UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605"), old={}, new={}
            )
        ],
    )

    hash_ = cart.get_id(b"\0" * 8, "0.1.0")
    assert hash_ == "a84e022390c29b9538dda8e6145b563dd0c32bdd546e61ad467bfa64a2bceccb"


def test_hash_any_order():
    cart1 = Cart(
        event_id="test",
        meta={"meta": "meta"},
        registrations=[
            CartRegistration(
                UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605"), old={}, new={}
            ),
            CartRegistration(
                UUID("f4a87b29-78b3-4f0b-bd3f-9de1f1a3409c"), old={}, new={}
            ),
        ],
    )
    cart2 = Cart(
        event_id="test",
        meta={"meta": "meta"},
        registrations=[
            CartRegistration(
                UUID("f4a87b29-78b3-4f0b-bd3f-9de1f1a3409c"), old={}, new={}
            ),
            CartRegistration(
                UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605"), old={}, new={}
            ),
        ],
    )

    hash1 = cart1.get_id(b"\0" * 8, "0.1.0")
    hash2 = cart2.get_id(b"\0" * 8, "0.1.0")
    assert hash1 == hash2


@pytest.mark.asyncio
async def test_add(service: CartService, session: AsyncSession):
    cart = Cart("test")
    entity1 = await service.add(cart)
    id = entity1.id
    await session.commit()

    entity2 = await service.add(cart)
    assert entity2.id == id


@pytest.mark.asyncio
async def test_add_no_update_created(service: CartService, session: AsyncSession):
    cart = Cart("test")
    entity1 = await service.add(cart)
    await session.flush()
    date_created = entity1.date_created
    await session.commit()

    entity2 = await service.add(cart)
    assert entity2.date_created == date_created


@pytest.mark.asyncio
async def test_cart_add_registration(
    service: CartService, session: AsyncSession, repo: CartRepo
):
    empty = Cart("test")
    empty_entity = await service.add(empty)
    empty_id = empty_entity.id
    await session.commit()

    empty_entity = await repo.get(empty_id)
    assert empty_entity
    result_entity = await service.add_to_cart(
        empty_entity, [CartRegistration(UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605"))]
    )
    result = result_entity.get_cart()
    assert result.registrations == [
        CartRegistration(UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605"))
    ]


@pytest.mark.asyncio
async def test_cart_add_registration_replace(
    service: CartService, session: AsyncSession, repo: CartRepo
):
    base = Cart(
        "test",
        registrations=[
            CartRegistration(UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605")),
            CartRegistration(UUID("f4a87b29-78b3-4f0b-bd3f-9de1f1a3409c")),
        ],
    )
    base_entity = await service.add(base)
    base_id = base_entity.id
    await session.commit()

    base_entity = await repo.get(base_id)
    assert base_entity

    result_entity = await service.add_to_cart(
        base_entity,
        [
            CartRegistration(UUID("bdb33e19-1373-4c65-80ee-ac7364329932")),
            CartRegistration(
                UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605"), new={"new": True}
            ),
        ],
    )
    result = result_entity.get_cart()
    assert result.registrations == [
        CartRegistration(
            UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605"), new={"new": True}
        ),
        CartRegistration(UUID("f4a87b29-78b3-4f0b-bd3f-9de1f1a3409c")),
        CartRegistration(UUID("bdb33e19-1373-4c65-80ee-ac7364329932")),
    ]


@pytest.mark.asyncio
async def test_cart_remove_registration(
    service: CartService, session: AsyncSession, repo: CartRepo
):
    base = Cart(
        "test",
        registrations=[
            CartRegistration(UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605")),
            CartRegistration(UUID("f4a87b29-78b3-4f0b-bd3f-9de1f1a3409c")),
        ],
    )
    base_entity = await service.add(base)
    base_id = base_entity.id
    await session.commit()

    base_entity = await repo.get(base_id)
    assert base_entity

    result_entity = await service.remove_from_cart(
        base_entity, UUID("c152e91e-5d8c-4219-a774-e2c7f08f9605")
    )
    result = result_entity.get_cart()
    assert result.registrations == [
        CartRegistration(UUID("f4a87b29-78b3-4f0b-bd3f-9de1f1a3409c")),
    ]
