# app/utils/llm_generator.py
import os
from typing import List, Dict, Any, Optional
import httpx
from app.models.product import Product
from app.config import settings

async def generate_ad_sheet_content(products: List[Product], platform: str, template: str) -> str:
    """
    Genera el contenido de una ficha publicitaria utilizando un LLM (OpenAI o Anthropic)
    
    Args:
        products: Lista de productos para incluir en la ficha
        platform: Plataforma destino (facebook, whatsapp, revolico)
        template: Plantilla a utilizar
        
    Returns:
        Contenido en markdown de la ficha publicitaria
    """
    # Preparar la información de los productos
    products_data = []
    for product in products:
        product_data = {
            "id": str(product.id),
            "nombre": product.nombre,
            "precio": float(product.precio),
            "color": product.color,
            "talla": product.talla,
            "caracteristicas": product.caracteristicas,
            "disponible": product.disponible,
            "foto": product.foto
        }
        products_data.append(product_data)
    
    # Definir los templates según la plataforma
    templates = {
        "facebook": {
            "basic": """
# 🛍️ {product_name}

📌 **Precio**: ${product_price}
{product_details}

✨ *¡Disponible ahora! Contáctanos para más información.*
            """,
            "detailed": """
# 🔥 OFERTA ESPECIAL 🔥

## {product_name}

![Imagen del producto]({product_image_url})

### Detalles:
- 💰 **Precio**: ${product_price}
{product_details}

### ¿Por qué elegir este producto?
{product_benefits}

📞 *¡Contáctanos ahora y no pierdas esta oportunidad!*
            """
        },
        "whatsapp": {
            "basic": """
*{product_name}*
💰 Precio: ${product_price}
{product_details}

✅ ¡Disponible para entrega inmediata!
🔄 Responde a este mensaje para más información
            """,
            "detailed": """
*🌟 NUEVO PRODUCTO 🌟*

*{product_name}*

💰 *Precio:* ${product_price}
{product_details}

📋 *Características destacadas:*
{product_benefits}

🚚 Entrega disponible
💳 Múltiples métodos de pago

_¡Pregunta por disponibilidad y más detalles!_
            """
        },
        "revolico": {
            "basic": """
# {product_name}

Precio: ${product_price}
{product_details}

Contacto: [NÚMERO]
            """,
            "detailed": """
# {product_name} - ${product_price}

![Imagen]({product_image_url})

## Descripción:
{product_details}

## Especificaciones:
{product_specifications}

## Detalles de contacto:
- Teléfono: [NÚMERO]
- Disponibilidad: [HORARIO]
- Ubicación: [LOCALIDAD]

_Se aceptan pagos en efectivo y transferencia._
            """
        }
    }
    
    # Seleccionar el template adecuado
    selected_template = templates.get(platform, {}).get(template, templates["facebook"]["basic"])
    
    # Construir el prompt para el LLM
    if settings.LLM_PROVIDER.lower() == "openai":
        return await generate_with_openai(products_data, platform, selected_template)
    else:
        return await generate_with_anthropic(products_data, platform, selected_template)

async def generate_with_openai(products_data: List[Dict[str, Any]], platform: str, template: str) -> str:
    """Genera contenido usando la API de OpenAI"""
    
    prompt = f"""
    Eres un experto en marketing digital y ventas. Necesito que crees una ficha publicitaria en formato markdown para los siguientes productos:
    
    ```json
    {products_data}
    ```
    
    La ficha publicitaria será publicada en {platform}.
    Usa el siguiente template como guía, pero puedes mejorarlo según las mejores prácticas de {platform}:
    
    ```
    {template}
    ```
    
    Por favor, crea una ficha atractiva, persuasiva y optimizada para la plataforma {platform}.
    Si la ficha es para varios productos, agrúpalos de forma coherente.
    Incluye emoji adecuados para hacerla atractiva.
    No incluyas URLs de imágenes falsas, solo referencias a las fotos mencionadas en los datos.
    Recuerda que el formato final debe ser markdown plano.
    """
    
    # Configurar la API de OpenAI
    api_key = settings.OPENAI_API_KEY
    
    # Llamar a la API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Error en la API de OpenAI: {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

async def generate_with_anthropic(products_data: List[Dict[str, Any]], platform: str, template: str) -> str:
    """Genera contenido usando la API de Anthropic"""
    
    prompt = f"""
    Eres un experto en marketing digital y ventas. Necesito que crees una ficha publicitaria en formato markdown para los siguientes productos:
    
    ```json
    {products_data}
    ```
    
    La ficha publicitaria será publicada en {platform}.
    Usa el siguiente template como guía, pero puedes mejorarlo según las mejores prácticas de {platform}:
    
    ```
    {template}
    ```
    
    Por favor, crea una ficha atractiva, persuasiva y optimizada para la plataforma {platform}.
    Si la ficha es para varios productos, agrúpalos de forma coherente.
    Incluye emoji adecuados para hacerla atractiva.
    No incluyas URLs de imágenes falsas, solo referencias a las fotos mencionadas en los datos.
    Recuerda que el formato final debe ser markdown plano.
    """
    
    # Configurar la API de Anthropic
    api_key = settings.ANTHROPIC_API_KEY
    
    # Llamar a la API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-3-opus-20240229",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Error en la API de Anthropic: {response.text}")
        
        data = response.json()
        return data["content"][0]["text"].strip()