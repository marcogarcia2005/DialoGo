from textblob import TextBlob  # type: ignore
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

# Inicializar la clave API de Gemini AI
API_KEY = "AIzaSyBl5XEAR5xySDybUBrv2bifYdll474gGvY"

# Configurar el modelo generativo de Gemini AI
gemini.configure(api_key=API_KEY)
model = gemini.GenerativeModel('gemini-1.5-flash')

def generate_response(user_input):
    # Generar respuesta con Gemini AI
    response = model.generate(
        prompt=user_input,
        max_tokens=50,   # Ajusta la longitud de la respuesta
        temperature=0.5, # Menos aleatoriedad para respuestas más coherentes
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # Extraer y retornar el texto generado
    generated_text = response.choices[0].text.strip()
    return generated_text

def correct_text(text):
    # Crear un objeto TextBlob y corregir el texto
    corrected_text = str(TextBlob(text).correct())
    
    # Retornar el texto corregido si es diferente, sino el original
    if corrected_text != text:
        return corrected_text
    return None

TOKEN = '7527809020:AAGL_3LusNvcDN6gy0FfuoQpteRMIKi3kqg' 

# Definir una función para empezar el bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '¡Hola! Soy tu bot de práctica de idiomas.\n'
        'Elige un tema para practicar tu inglés:\n'
        '1. Saludos\n'
        '2. Descripciones personales\n'
        '3. Hobbies\n'
        '4. Avances de la tecnología\n'
        'Escribe el número del tema que te gustaría practicar.'
    )
    
    # Programar el recordatorio cada 10 minutos
    context.job_queue.run_repeating(send_reminder, interval=600, first=0, data=update.message.chat_id)

# Función que envía el recordatorio
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    await context.bot.send_message(chat_id, "¡Es hora de practicar tu inglés!")

# Función que maneja los mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Si el usuario selecciona un tema
    if user_message in ["1", "2", "3", "4"]:
        topic_responses = {
            "1": "¡Genial! Vamos a practicar saludos. ¿Cómo dirías 'Hola' en inglés?",
            "2": "¡Genial! Vamos a practicar descripciones personales. ¿Cómo te describirías en inglés?",
            "3": "¡Genial! Vamos a hablar sobre hobbies. ¿Cuál es tu hobby favorito en inglés?",
            "4": "¡Genial! Vamos a hablar sobre los avances de la tecnología. ¿Qué avances tecnológicos te interesan?"
        }
        await update.message.reply_text(topic_responses[user_message])
    else:
        # Corrección automática del texto del usuario
        corrected_message = correct_text(user_message)
        if corrected_message:
            await update.message.reply_text(f"¿Quisiste decir?: {corrected_message}")
            user_message = corrected_message
        
        # Generar respuesta con Gemini AI
        response = generate_response(user_message)
        await update.message.reply_text(response)

        # Mensajes de depuración para verificar la entrada y salida
        print(f"Texto ingresado: {user_message}")
        print(f"Respuesta generada: {response}")

# Función principal para inicializar el bot
def main():
    # Crear la aplicación (bot) con el token
    if TOKEN is None:
        raise ValueError("El token de Telegram no está definido. Asegúrate de configurarlo como una variable de entorno.")

    application = Application.builder().token(TOKEN).build()

    # Añadir manejadores de comandos y mensajes
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()
