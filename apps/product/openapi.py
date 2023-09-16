from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status

from apps.product.cart_serializers import (
    CartItemCreateSerializer,
    CartModelSerializer,
    FavoriteCreateSerializer,
    FavoriteSerializer,
)

cart_items = extend_schema(responses={status.HTTP_200_OK: CartModelSerializer}, methods=['GET'])
add_cartitem = extend_schema(
    request=CartItemCreateSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=CartModelSerializer, description='Успешное добавление товара в корзину'
        )
    },
    methods=['POST'],
)
delete_cartitem = extend_schema(
    parameters=[OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Идентификатор продукта')],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=CartModelSerializer, description='Успешное удаление товара из корзины'
        )
    },
    methods=['DELETE'],
)
favorite_list = extend_schema(responses={status.HTTP_200_OK: FavoriteSerializer}, methods=['GET'])
add_favorite = extend_schema(
    request=FavoriteCreateSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=FavoriteSerializer, description='Успешное добавление товара в избранное'
        )
    },
    methods=['POST'],
)
delete_favorite = extend_schema(
    parameters=[OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Идентификатор продукта')],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=FavoriteSerializer, description='Успешное удаление товара из избранного'
        )
    },
    methods=['DELETE'],
)
