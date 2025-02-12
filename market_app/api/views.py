from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import MarketSerializer, SellerDetailSerializer, \
    SellerCreateSerializer, ProductDetailSerializer, ProductCreateSerializer, SellerSerializer, \
    MarketHyperlinkedSerializer, ProductSerializer, ProductHyperlinkedSerializer, SellerListSerializer
from market_app.models import Market, Seller, Product
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics

from django.shortcuts import get_object_or_404
from rest_framework import viewsets


class MarketsView(generics.ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer


""" generic class-based views: GenericAPIView with Mixins"""
# class MarketsView(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   generics.GenericAPIView):
#     queryset = Market.objects.all()
#     serializer_class = MarketSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
    
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


@api_view(['GET', 'POST'])
def markets_view(request):

    if request.method == 'GET':
        markets = Market.objects.all()
        serializer = MarketHyperlinkedSerializer(markets, many=True, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = MarketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

        # try:
        #     msg = request.data['message']
        #     return Response({"your_message": msg}, status=status.HTTP_201_CREATED)
        # except Exception:
        #     return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


# class SellerOfMarketList(generics.ListAPIView):
#     serializer_class = SellerSerializer

#     def get_queryset(self):
#         pk = self.kwargs.get('pk')
#         market = Market.objects.get(pk=pk)
#         return market.sellers.all()


class SellerOfMarketList(generics.ListCreateAPIView):
    serializer_class = SellerListSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        market = Market.objects.get(pk=pk)
        return market.sellers.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        market = Market.objects.get(pk=pk)
        serializer.save(markets=[market])


class MarketSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer


# class MarketSingleView(mixins.RetrieveModelMixin,
#                        mixins.UpdateModelMixin,
#                        mixins.DestroyModelMixin,
#                        generics.GenericAPIView):
#     queryset = Market.objects.all()
#     serializer_class = MarketSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return self.update(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)


@api_view(['GET', 'DELETE', 'PUT'])
def market_single_view(request, pk):
    
    if request.method == 'GET':
        market = Market.objects.get(pk=pk)
        serializer = MarketSerializer(market, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'PUT':
        market = Market.objects.get(pk=pk)
        serializer = MarketSerializer(market, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    
    if request.method == 'DELETE':
        market = Market.objects.get(pk=pk)
        serializer = MarketSerializer(market)
        market.delete()
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def sellers_view(request):

    if request.method == 'GET':
        sellers = Seller.objects.all()
        serializer = SellerSerializer(sellers, many=True, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = SellerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

@api_view()
def seller_single_view(request, pk):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=pk)
        serializer = SellerSerializer(seller, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):
    queryset = Product.objects.all()

    def list(self, request):
        serializer = ProductSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = ProductSerializer(user)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def products_view(request):

    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductHyperlinkedSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = ProductHyperlinkedSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'PUT'])
def product_single_view(request, pk):
    
    if request.method == 'GET':
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data)
        except Exception:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            # return redirect('/api/product/')
    
    if request.method == 'PUT':
        product = Product.objects.get(pk=pk)
        serializer = ProductHyperlinkedSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    
    if request.method == 'DELETE':
        product = Product.objects.get(pk=pk)
        serializer = ProductHyperlinkedSerializer(product, context={'request': request})
        product.delete()
        return Response(serializer.data)
