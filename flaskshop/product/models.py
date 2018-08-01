import json
from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property

from flaskshop.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)


class Product(SurrogatePK, Model):
    __tablename__ = "product_product"
    title = Column(db.String(255), nullable=False)
    description = Column(db.Text())
    on_sale = Column(db.Boolean(), default=True)
    rating = Column(db.DECIMAL(8, 2), default=5.0)
    sold_count = Column(db.Integer(), default=0)
    review_count = Column(db.Integer(), default=0)
    price = Column(db.DECIMAL(10, 2))
    category_id = reference_col("product_category")
    category = relationship("Category")
    is_featured = Column(db.Boolean(), default=False)
    product_type_id = reference_col("product_producttype")
    product_type = relationship("ProductType", backref="products")
    _attributes = Column("attributes", db.Text())

    def __str__(self):
        return self.title

    @hybrid_property
    def attributes(self):
        if self._attributes:
            return {int(k): v for k, v in json.loads(self._attributes).items()}
        else:
            return dict()

    @attributes.setter
    def attributes(self, value):
        if isinstance(value, dict):
            if self._attributes:
                old_attr = json.loads(self._attributes)
                old_attr.update(value)
                self._attributes = json.dumps(old_attr)
            else:
                self._attributes = json.dumps(value)
        else:
            raise Exception("Must set a dict for product attribute")

    @property
    def get_absolute_url(self):
        return url_for("product.show", id=self.id)

    @property
    def get_first_img(self):
        if self.images:
            return self.images[0]
        return ""

    def to_dict(self):
        res = super().to_dict()
        res['first_img'] = self.get_first_img
        return res



class Category(SurrogatePK, Model):
    __tablename__ = "product_category"
    title = Column(db.String(255), nullable=False)
    parent_id = reference_col("product_category")
    background_img = Column(db.String(255))
    products = relationship("Product", lazy="dynamic")

    def __str__(self):
        return self.title

    @property
    def get_absolute_url(self):
        return url_for("product.show_category", id=self.id)


Category.parent = relationship("Category", backref="children", remote_side=Category.id)

product_type_product_attrbuites = db.Table(
    "product_producttype_product_attributes",
    Column("id", db.Integer(), primary_key=True, autoincrement=True),
    Column(
        "producttype_id",
        db.Integer(),
        db.ForeignKey("product_producttype.id"),
        primary_key=True,
    ),
    Column(
        "productattribute_id",
        db.Integer(),
        db.ForeignKey("product_productattribute.id"),
        primary_key=True,
    ),
)

product_type_variant_attrbuites = db.Table(
    "product_producttype_variant_attributes",
    Column("id", db.Integer(), primary_key=True, autoincrement=True),
    Column(
        "producttype_id",
        db.Integer(),
        db.ForeignKey("product_producttype.id"),
        primary_key=True,
    ),
    Column(
        "productattribute_id",
        db.Integer(),
        db.ForeignKey("product_productattribute.id"),
        primary_key=True,
    ),
)


class ProductType(SurrogatePK, Model):
    __tablename__ = "product_producttype"
    title = Column(db.String(255), nullable=False)
    has_variants = Column(db.Boolean(), default=True)
    is_shipping_required = Column(db.Boolean(), default=False)
    product_attributes = relationship(
        "ProductAttribute",
        secondary=product_type_product_attrbuites,
        backref="product_types",
        lazy="dynamic",
    )
    variant_attributes = relationship(
        "ProductAttribute",
        secondary=product_type_variant_attrbuites,
        backref="variant_types",
        lazy="dynamic",
    )


class ProductVariant(SurrogatePK, Model):
    __tablename__ = "product_variant"
    sku = Column(db.String(32), unique=True)
    title = Column(db.String(255))
    price_override = Column(db.DECIMAL(10, 2))
    quantity = Column(db.Integer())
    product_id = reference_col("product_product")
    product = relationship("Product", backref="variant")
    _attributes = Column("attributes", db.String(255))

    def __str__(self):
        return self.title if self.title else self.product.title

    @hybrid_property
    def attributes(self):
        if self._attributes:
            return {int(k): v for k, v in json.loads(self._attributes).items()}
        else:
            return dict()

    @attributes.setter
    def attributes(self, value):
        if isinstance(value, dict):
            if self._attributes:
                old_attr = json.loads(self._attributes)
                old_attr.update(value)
                self._attributes = json.dumps(old_attr)
            else:
                self._attributes = json.dumps(value)
        else:
            raise Exception("Must set a dict for product attribute")

    @property
    def price(self):
        return self.price_override if self.price_override else self.product.price


class ProductAttribute(SurrogatePK, Model):
    __tablename__ = "product_productattribute"
    title = Column(db.String(255), nullable=False)

    def __str__(self):
        return self.title


class AttributeChoiceValue(SurrogatePK, Model):
    __tablename__ = "product_attributechoicevalue"
    title = Column(db.String(255), nullable=False)
    attribute_id = reference_col("product_productattribute")
    attribute = relationship("ProductAttribute", backref="values")

    def __str__(self):
        return self.title


class ProductImage(SurrogatePK, Model):
    __tablename__ = "product_productimage"
    image = Column(db.String(255))
    order = Column(db.Integer())
    product_id = reference_col("product_product")
    product = relationship("Product", backref="images")

    def __str__(self):
        return url_for("static", filename=self.image, _external=True)


product_collection = db.Table(
    "product_collection_products",
    Column("id", db.Integer(), primary_key=True, autoincrement=True),
    Column(
        "product_id",
        db.Integer(),
        db.ForeignKey("product_product.id"),
        primary_key=True,
    ),
    Column(
        "collection_id", db.Integer(), db.ForeignKey("product_collection.id"), primary_key=True
    ),
)


class Collection(SurrogatePK, Model):
    __tablename__ = "product_collection"
    title = Column(db.String(255), nullable=False)
    background_img = Column(db.String(255))
    products = relationship("Product", secondary=product_collection, lazy="dynamic")

    def __str__(self):
        return self.title

    @property
    def get_absolute_url(self):
        return url_for("product.show_collection", id=self.id)
