from sqlalchemy.orm import Session

from . import models

# 公开图床占位图（演示用，接单可换真实上传）
COVERS = {
    "草莓": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400&h=400&fit=crop",
    "鸡蛋": "https://images.unsplash.com/photo-1582722872448-8a0d0a63c5b2?w=400&h=400&fit=crop",
    "豆浆": "https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400&h=400&fit=crop",
}


def seed_if_empty(db: Session) -> None:
    if db.query(models.Product).count() == 0:
        db.add_all(
            [
                models.Product(
                    name="红颜草莓 1 斤",
                    desc="当季现摘，甜度高，适合家庭分享。",
                    price_cents=2880,
                    stock=50,
                    cover_url=COVERS["草莓"],
                ),
                models.Product(
                    name="土鸡蛋 20 枚",
                    desc="散养土鸡，蛋黄金黄。",
                    price_cents=2590,
                    stock=80,
                    cover_url=COVERS["鸡蛋"],
                ),
                models.Product(
                    name="现磨豆浆 1L",
                    desc="当日现磨，无添加。",
                    price_cents=1200,
                    stock=40,
                    cover_url=COVERS["豆浆"],
                ),
            ]
        )
    else:
        # 旧库补封面（仅空封面时）
        for p in db.query(models.Product).all():
            if p.cover_url:
                continue
            for key, url in COVERS.items():
                if key in p.name:
                    p.cover_url = url
                    break
    if db.query(models.PickupPoint).count() == 0:
        db.add_all(
            [
                models.PickupPoint(name="阳光花园东门驿站", address="阳光花园东门快递柜旁"),
                models.PickupPoint(name="邻里便利店", address="幸福路 18 号便利店柜台"),
            ]
        )
    db.commit()
