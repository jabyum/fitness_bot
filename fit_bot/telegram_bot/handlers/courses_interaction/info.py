from telebot.types import Message
from telebot import custom_filters
from django.utils import timezone


from ...loader import bot
from ...states import CourseInteraction
from courses.models import Категории, Content, Mailing, Training
from ...models import PaidUser
from ..mainmenu import get_id


@bot.message_handler(state=CourseInteraction.initial, func=lambda message: message.text == 'Получить тренировки 🎾')
def get_courses(message: Message):
    user_id, chat_id = get_id(message=message)
    user = PaidUser.objects.filter(user=user_id).first()

    try:
        matching_category = Категории.objects.get(
            пол=user.пол,
            цель=user.цель,
            место=user.место,
            уровень=user.уровень
        )

        delta_days = (timezone.now().date() - user.paid_day).days
        current_day = delta_days

        daily_contents = Training.objects.filter(category=matching_category, day=current_day)
        if daily_contents:
            for content in daily_contents:
                updated_caption = content.caption.replace("calories", str(user.calories)).replace("name",
                                                                                                  user.full_name)
                if content.content_type == 'V':
                    video_file_id = content.video.video_file_id
                    bot.send_video(chat_id=user.user, video=video_file_id, caption=updated_caption)
                elif content.content_type == 'T':
                    bot.send_message(chat_id=user.user, text=updated_caption)
                elif content.content_type == 'P':
                    bot.send_photo(chat_id=user.user, photo=content.photo_file_id, caption=updated_caption)
                elif content.content_type == 'G':
                    bot.send_document(chat_id=user.user, document=content.gif_file_id, caption=updated_caption)
        else:
            bot.send_message(chat_id=user.user, text='Кажется, что на сегодня для вас нет тренировок! '
                                                     'Cледуйте инструкциям')
    except:
        bot.send_message(chat_id=user.user,
                         text='Кажется, что на сегодня для вас нет тренировок! следуйте инструкциям')


bot.add_custom_filter(custom_filters.StateFilter(bot))

