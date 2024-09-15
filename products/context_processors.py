from baskets.models import Basket

def basket(request):
   basket = []

   if request.user.is_authenticated:
       basket = Basket.objects.filter(user=request.user)

   return {
    'basket': basket,
   }