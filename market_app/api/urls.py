from django.urls import path, include
from .views import markets_view, market_single_view, sellers_view, \
    products_view, product_single_view, seller_single_view, MarketsView, \
    MarketSingleView, SellerOfMarketList, ProductViewSet, SellersView, SellerSingleView, \
    SellerViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'products', ProductViewSet)
router.register(r'sellers', SellerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('market/', MarketsView.as_view()),
    path('market/<int:pk>/', MarketSingleView.as_view(), name='market-detail'),
    path('market/<int:pk>/sellers/', SellerOfMarketList.as_view(), name='market-detail'),
    # path('seller/', SellersView.as_view()),
    # path('seller/<int:pk>/', SellerSingleView.as_view(), name='seller-detail'),
    # path('product/', products_view),
    # path('product/<int:pk>/', product_single_view, name='product-detail')
]
