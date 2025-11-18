from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import os
import json
import logging
from datetime import datetime
from .models import NgrokConfig, ChatMessage

logger = logging.getLogger(__name__)

def get_ngrok_api_url():
    """Lấy Ngrok API URL từ database hoặc environment"""
    # Ưu tiên database trước
    url = NgrokConfig.get_active_url()
    if url:
        return url
    # Fallback sang environment variable
    return os.getenv('NGROK_LLM_API', 'https://yyyyy.ngrok-free.app/ask')

# Health check cache
health_cache = {'last_check': None, 'status': None}

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    API Endpoint: POST /chatbot/api/chat/
    Request: {"query": "bao nhiêu đạm có trong gà?"}
    Response: {"success": true, "response": "...", "timestamp": "..."}
    """
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return JsonResponse({
                'success': False,
                'error': 'Query không được trống',
                'code': 'EMPTY_QUERY'
            }, status=400)
        
        if len(user_query) > 500:
            return JsonResponse({
                'success': False,
                'error': 'Câu hỏi quá dài (tối đa 500 ký tự)',
                'code': 'QUERY_TOO_LONG'
            }, status=400)
        
        logger.info(f"🔄 Chat request: {user_query[:50]}...")
        
        # Lấy Ngrok API URL từ database
        ngrok_api_url = get_ngrok_api_url()
        
        # 🔗 Gọi Colab LLM Backend qua Ngrok
        try:
            response = requests.post(
                ngrok_api_url,
                json={'query': user_query},
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            llm_data = response.json()
            bot_response = llm_data.get('answer', 'Không có câu trả lời từ LLM')
            
            logger.info(f"✅ LLM response: {bot_response[:100]}...")
            # Save chat history (optional) so admin can review conversations
            try:
                ChatMessage.objects.create(user_message=user_query, bot_response=bot_response)
            except Exception:
                logger.exception("Không thể lưu ChatMessage (bỏ qua)")

            # Include source metadata (useful for frontend display)
            source_label = ngrok_api_url or 'LLM'

            return JsonResponse({
                'success': True,
                'response': bot_response,
                'timestamp': datetime.now().isoformat(),
                'source': source_label,
                'code': 'LLM_SUCCESS'
            })
            
        except requests.exceptions.Timeout:
            logger.error("❌ LLM Timeout")
            return JsonResponse({
                'success': False,
                'error': '⏱️ Colab LLM đang xử lý chậm, vui lòng thử lại',
                'code': 'TIMEOUT',
                'hint': 'Hãy chắc chắn Colab đang chạy và Ngrok tunnel còn sống'
            }, status=504)
            
        except requests.exceptions.ConnectionError:
            logger.error("❌ LLM Connection Error")
            return JsonResponse({
                'success': False,
                'error': '📡 Ngrok offline - Colab backend không kết nối được',
                'code': 'CONNECTION_ERROR',
                'hint': 'Hãy kiểm tra Colab và tạo Ngrok tunnel mới'
            }, status=503)
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ LLM HTTP Error: {e}")
            return JsonResponse({
                'success': False,
                'error': f'🚨 LLM trả về lỗi: {e.response.status_code}',
                'code': 'LLM_HTTP_ERROR'
            }, status=502)
            
        except (json.JSONDecodeError, KeyError):
            logger.error("❌ Invalid LLM response format")
            return JsonResponse({
                'success': False,
                'error': '❌ Định dạng response từ LLM không hợp lệ',
                'code': 'INVALID_RESPONSE'
            }, status=502)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Request JSON không hợp lệ',
            'code': 'JSON_ERROR'
        }, status=400)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Lỗi server: {str(e)}',
            'code': 'SERVER_ERROR'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    API Endpoint: GET /chatbot/health/
    Kiểm tra kết nối với Colab LLM
    """
    try:
        ngrok_api_url = get_ngrok_api_url()
        response = requests.get(
            ngrok_api_url.replace('/ask', '/health'),
            timeout=5
        )
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'status': 'healthy',
                'message': '✅ Colab LLM online',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return JsonResponse({
                'success': False,
                'status': 'unhealthy',
                'message': f'⚠️ LLM trả về status {response.status_code}'
            }, status=503)
            
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return JsonResponse({
            'success': False,
            'status': 'offline',
            'message': '❌ Ngrok offline - Không kết nối được Colab',
            'ngrok_url': get_ngrok_api_url()
        }, status=503)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def update_ngrok_url(request):
    """
    API Endpoint: POST /chatbot/update-ngrok/
    Cập nhật Ngrok URL (trong production, thêm authentication)
    Request: {"ngrok_url": "https://xxxxx.ngrok-free.app/ask"}
    """
    global NGROK_LLM_API
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_url = data.get('ngrok_url', '').strip()
            
            if not new_url or not new_url.startswith('https'):
                return JsonResponse({
                    'success': False,
                    'error': 'URL không hợp lệ'
                }, status=400)
            
            NGROK_LLM_API = new_url
            os.environ['NGROK_LLM_API'] = new_url
            
            logger.info(f"✅ Ngrok URL cập nhật: {new_url}")
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Ngrok URL cập nhật: {new_url}',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    else:  # GET
        return JsonResponse({
            'current_ngrok_url': NGROK_LLM_API,
            'timestamp': datetime.now().isoformat()
        })
