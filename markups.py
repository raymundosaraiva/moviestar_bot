from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update


feedback_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='\U0001F44D Gostei', callback_data='feedback_liked'),
     InlineKeyboardButton(text='\U0001F44E Não Gostei', callback_data='feedback_disliked')]
])

after_feedback_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Próximo', callback_data='recommend_next')],
    [InlineKeyboardButton(text='Finalizar ', callback_data='recommend_end')],
])

similar_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Confirmar', callback_data='similar_confirm'),
     InlineKeyboardButton(text='Cancelar', callback_data='similar_cancel')]
])

genre_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton('Ação', callback_data='genre_28'),
     InlineKeyboardButton('Animação', callback_data='genre_16')],
    [InlineKeyboardButton('Comédia', callback_data='genre_35'),
     InlineKeyboardButton('Drama', callback_data='genre_18')],
    [InlineKeyboardButton('Fantasia', callback_data='genre_14'),
     InlineKeyboardButton('Terror', callback_data='genre_27')],
    [InlineKeyboardButton('Ficção', callback_data='genre_878'),
     InlineKeyboardButton('Suspense', callback_data='genre_53')]
])