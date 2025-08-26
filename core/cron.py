
from .models import quizresult

def reset_leaderboard():
    quizresult.objects.all().delete()
    print("✅ Leaderboard has been reset to zero for all users.")
