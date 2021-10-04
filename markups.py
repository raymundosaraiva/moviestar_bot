from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update

consent_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='\U0001F44D Desejo participar', callback_data='consent_agree'),
     InlineKeyboardButton(text='\U0001F44E Não tenho interesse', callback_data='consent_disagree')]
])

feedback_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='\U0001F44D Gostei', callback_data='feedback_liked'),
    InlineKeyboardButton(text='\U0001F44E Não Gostei', callback_data='feedback_disliked')]
])

after_feedback_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Próximo', callback_data='recommend_next')],
    [InlineKeyboardButton(text='Finalizar', callback_data='recommend_end')],
])

bandit_feedback_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='\U0001F503 Baseadas no Histórico', callback_data='bandit_exploit')],
    [InlineKeyboardButton(text='\U0001F50D Explorar Diversificadas', callback_data='bandit_explore')],
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

sex_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Masculino', callback_data='sex_masculine')],
    [InlineKeyboardButton(text='Feminino', callback_data='sex_feminine')],
    [InlineKeyboardButton(text='Outro', callback_data='sex_other')],
    [InlineKeyboardButton(text='Prefiro não dizer', callback_data='sex_na')]
])

age_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Até 17 anos', callback_data='age_1')],
    [InlineKeyboardButton(text='18 até 24 anos', callback_data='age_2')],
    [InlineKeyboardButton(text='25 até 34 anos', callback_data='age_3')],
    [InlineKeyboardButton(text='35 até 44 anos', callback_data='age_4')],
    [InlineKeyboardButton(text='45 até 59 anos', callback_data='age_5')],
    [InlineKeyboardButton(text='60 anos e acima', callback_data='age_6')]
])
