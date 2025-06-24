from datetime import date
from .models import DailyFact

def daily_fact(request):
    today = date.today()
    fact = DailyFact.objects.filter(date=today).first()
    return {'daily_fact': fact}