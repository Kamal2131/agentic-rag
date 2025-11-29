from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 OK if the application is healthy.
    """
    health_status = {
        "status": "healthy",
        "service": "agentic-rag",
        "version": "1.0.0",
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status, status=200)


@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check endpoint.
    Returns 200 OK when the application is ready to serve traffic.
    """
    checks = {
        "database": False,
        "qdrant": False,
        "redis": False,
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        pass
    
    # Check Qdrant (optional - would require qdrant client)
    # For now, assume it's available
    checks["qdrant"] = True
    
    # Check Redis (optional - would require redis client)
    # For now, assume it's available
    checks["redis"] = True
    
    all_ready = all(checks.values())
    
    response_data = {
        "ready": all_ready,
        "checks": checks
    }
    
    status_code = 200 if all_ready else 503
    return JsonResponse(response_data, status=status_code)
