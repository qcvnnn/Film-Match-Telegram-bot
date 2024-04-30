import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from dotenv import load_dotenv
import os
from sqlalchemy.sql import exists
from database.database import session
from database.models.user import User
from database.models.room import Room
from database.models.match import Match
from database.models.film import Film
from random import randint

load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), parse_mode="html")

@bot.message_handler(['start'])
def start(message):
    if not session.query(exists().where(User.user_id == message.from_user.id)).scalar():
        new_user = User(
            user_id = message.from_user.id,
            username = message.from_user.username
        )
        session.add(new_user)
        session.commit()

    bot.send_message(message.from_user.id, "<b>Добро пожаловать в бота по подбору фильмов для вас и ваших близких.</b>🌸", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔎 Начать выбор", callback_data="startSearch")
    ))

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "startSearch":
        bot.edit_message_text("<b>Вы можете создать свою комнату либо войти в уже существующую с помощью кода.🌟</b>", call.from_user.id, call.message.id, reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("➕ Создать комнату", callback_data="createRoom"),
            InlineKeyboardButton("🔗 Присоединиться", callback_data="connectRoom")
        ))

        bot.answer_callback_query(call.id)
    if call.data == "createRoom":
        roomid = randint(10000000, 99999999)
        new_room = Room(
            key = roomid,
            user1 = call.from_user.id
        ) 

        session.add(new_room)
        session.commit()

        bot.edit_message_text(f"ID комнаты: {roomid}\n<b>Отправьте его вашему партнеру, чтобы он мог присоединиться</b>", call.from_user.id, call.message.id)

        bot.answer_callback_query(call.id)

    if call.data == "connectRoom":
        bot.edit_message_text("Введите <b>код комнаты.</b>", call.from_user.id, call.message.id)
        bot.register_next_step_handler_by_chat_id(call.from_user.id, connectRoom)

    if call.data.split("_")[0] == "likeFilm":
        try:
            match = session.query(Match).where(
                Match.room_id == call.data.split("_")[1],
                Match.film_id == call.data.split("_")[2],
            ).one()
            
            if call.data.split("_")[3] == "1" and match.user2_vote == True or (call.data.split("_")[3] == "2" and match.user1_vote == True):
                film = session.query(Film).where(
                    Film.id == call.data.split("_")[2],
                ).one()

                room = session.query(Room).where(
                    Room.id == call.data.split("_")[1],
                ).one()

                bot.send_message(room.user1, f"У вас случился <b>мэтч!</b>💫 Фильм <b><u>{film.name}</u></b>", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Открыть на Кинопоиске", url=f"https://www.kinopoisk.ru/film/{film.kpid}/")))                
                bot.send_message(room.user2, f"У вас случился <b>мэтч!</b>💫 Фильм <b><u>{film.name}</u></b>", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Открыть на Кинопоиске", url=f"https://www.kinopoisk.ru/film/{film.kpid}/")))                

            else:
                raise

        except Exception as e:
            if call.data.split("_")[3] == "1":
                new_match = Match(
                    room_id = call.data.split("_")[1],
                    film_id = call.data.split("_")[2],
                    user1_vote = True
                )
            elif call.data.split("_")[3] == "2":
                new_match = Match(
                    room_id = call.data.split("_")[1],
                    film_id = call.data.split("_")[2],
                    user2_vote = True
                )

            session.add(new_match)
            session.commit()

            try:
                film = session.query(Film).where(
                    Film.id == int(call.data.split("_")[2])+1
                ).one()
                
                bot.answer_callback_query(call.id, "🟢 Голос учтен")
                bot.delete_message(call.from_user.id, call.message.id)

                bot.send_photo(
                    call.from_user.id, 
                    film.image,
                    f"<b>{film.name}</b>\n\n"+
                    f"<b>Жанры:</b> {film.genre}\n\n"+
                    f"<i>{film.description}</i>\n\n"
                    f"<b>⭐️Рейтинг:</b>\n"
                    f"<b>IMDB:</b> {film.rating_imdb}\n"+
                    f"<b>Кинопоиск:</b> {film.rating_kp}\n",

                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("👍", callback_data=f"likeFilm_{call.data.split('_')[1]}_{film.id}_{call.data.split('_')[3]}"),
                        InlineKeyboardButton("👎", callback_data=f"dislikeFilm_{call.data.split('_')[1]}_{film.id}_{call.data.split('_')[3]}")
                    )
                )

            except Exception as e:
                bot.delete_message(call.from_user.id, call.message.id)
                bot.send_message(call.from_user.id, "<b>У нас закончились фильмы. Если ваш партнер закончил и получил такое же сообщение, значит у вас не случился мэтч :( Возможно вам стоит немного снизить требования и создать новую комнату</b>")

        
    if call.data.split("_")[0] == "dislikeFilm":
        if call.data.split("_")[3] == "1":
            new_match = Match(
                room_id = call.data.split("_")[1],
                film_id = call.data.split("_")[2],
                user1_vote = False
            )
        elif call.data.split("_")[3] == "2":
            new_match = Match(
                room_id = call.data.split("_")[1],
                film_id = call.data.split("_")[2],
                user2_vote = False
            )

        session.add(new_match)
        session.commit()

        try:
            film = session.query(Film).where(
                Film.id == int(call.data.split("_")[2])+1
            ).one()
            
            bot.answer_callback_query(call.id, "🟢 Голос учтен")
            bot.delete_message(call.from_user.id, call.message.id)

            bot.send_photo(
                call.from_user.id, 
                film.image,
                f"<b>{film.name}</b>\n\n"+
                f"<b>Жанры:</b> {film.genre}\n\n"+
                f"<i>{film.description}</i>\n\n"
                f"<b>⭐️Рейтинг:</b>\n"
                f"<b>IMDB:</b> {film.rating_imdb}\n"+
                f"<b>Кинопоиск:</b> {film.rating_kp}\n",

                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("👍", callback_data=f"likeFilm_{call.data.split('_')[1]}_{film.id}_{call.data.split('_')[3]}"),
                    InlineKeyboardButton("👎", callback_data=f"dislikeFilm_{call.data.split('_')[1]}_{film.id}_{call.data.split('_')[3]}")
                )
            )

        except Exception as e:
            bot.delete_message(call.from_user.id, call.message.id)
            bot.send_message(call.from_user.id, "<b>У нас закончились фильмы. Если ваш партнер закончил и получил такое же сообщение, значит у вас не случился мэтч :( Возможно вам стоит немного снизить требования и создать новую комнату</b>")


def connectRoom(message):
    try:
        room = session.query(Room).where(
            Room.key == message.text
        ).one()

        room.user2 = message.from_user.id
        session.add(room)
        session.commit()

        bot.send_message(room.user1, "Выбор фильма начат!")
        bot.send_message(room.user2, "Выбор фильма начат!")

        film = session.query(Film).where(
            Film.id == 1
        ).one()

        bot.send_photo(
            message.from_user.id, 
            film.image,
            f"<b>{film.name}</b>\n\n"+
            f"<b>Жанры:</b> {film.genre}\n\n"+
            f"<i>{film.description}</i>\n\n"
            f"<b>⭐️Рейтинг:</b>\n"
            f"<b>IMDB:</b> {film.rating_imdb}\n"+
            f"<b>Кинопоиск:</b> {film.rating_kp}\n",

            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("👍", callback_data=f"likeFilm_{room.id}_{film.id}_2"),
                InlineKeyboardButton("👎", callback_data=f"dislikeFilm_{room.id}_{film.id}_2")
            )
        )

        bot.send_photo(
            room.user1, 
            film.image,
            f"<b>{film.name}</b>\n\n"+
            f"<b>Жанры:</b> {film.genre}\n\n"+
            f"<i>{film.description}</i>\n\n"
            f"<b>⭐️Рейтинг:</b>\n"
            f"<b>IMDB:</b> {film.rating_imdb}\n"+
            f"<b>Кинопоиск:</b> {film.rating_kp}\n",

            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("👍", callback_data=f"likeFilm_{room.id}_{film.id}_1"),
                InlineKeyboardButton("👎", callback_data=f"dislikeFilm_{room.id}_{film.id}_1")
            )
        )

    except Exception as e:
        bot.send_message(message.from_user.id, "Комната <i>не найдена</i>.")
    

bot.polling(non_stop=True)