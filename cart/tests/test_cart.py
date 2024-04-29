import pytest
from oes.cart.cart import Cart, CartRepo, CartService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def service(session: AsyncSession):
    return CartService(CartRepo(session), b"\0" * 8, "0.1.0")


def test_hash():
    cart = Cart(
        event_id="test",
        meta={"meta": "meta"},
        registrations=[
            {
                "event_id": "test",
            }
        ],
    )

    hash_ = cart.get_id(b"\0" * 8, "0.1.0")
    assert hash_ == "b92aae5bb14a4fd483b271281bf0e540d22b608f761a9b980a0814bbfdd52c51"


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
async def test_cart_parent(service: CartService, session: AsyncSession):
    cart1 = Cart("test")
    entity1 = await service.add(cart1)
    id1 = entity1.id
    await session.commit()

    cart2 = Cart("test", meta={"cart": 2})
    entity2 = await service.add(cart2, id1)
    id2 = entity2.id
    await session.commit()

    entity1 = await service.add(cart1)
    await session.refresh(entity1, ["children"])
    assert len(entity1.children) == 1
    assert entity1.children[0].id == id2
