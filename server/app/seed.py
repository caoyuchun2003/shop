from sqlalchemy.orm import Session

from . import models


def seed_if_empty(db: Session) -> None:
    if db.query(models.Product).count() == 0:
        db.add_all(
            [
                models.Product(
                    name="红颜草莓 1 斤",
                    desc="当季现摘，甜度高，适合家庭分享。",
                    price_cents=2880,
                    stock=50,
                    cover_url="",
                ),
                models.Product(
                    name="土鸡蛋 20 枚",
                    desc="散养土鸡，蛋黄金黄。",
                    price_cents=2590,
                    stock=80,
                    cover_url="",
                ),
                models.Product(
                    name="现磨豆浆 1L",
                    desc="当日现磨，无添加。",
                    price_cents=1200,
                    stock=40,
                    cover_url="",
                ),
            ]
        )
    if db.query(models.PickupPoint).count() == 0:
        db.add_all(
            [
                models.PickupPoint(name="阳光花园东门驿站", address="阳光花园东门快递柜旁"),
                models.PickupPoint(name="邻里便利店", address="幸福路 18 号便利店柜台"),
            ]
        )
    db.commit()
