from .models import Log


def create_log(request, line_user_id, keyword):
    log = Log.objects.create(line_user_id=line_user_id, keyword=keyword)
    
    return log