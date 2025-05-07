from telegram import Update, KeyboardButton,ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import json

usersData = []
dataFile = open ("User_Data.json", "r", encoding="utf-8")
usersData = json.load(dataFile)
dataFile.close()

admins = []
dataFile = open ("Admin.json", "r")
admins = json.load(dataFile)
dataFile.close()

courses = {}
dataFile = open ("Courses.json", "r", encoding="utf-8")
courses = json.load(dataFile)
dataFile.close()


def saveLastData():
    dataFile = open ("User_Data.json", "w")
    dataFile.write(json.dumps(usersData))
    dataFile.close()

    dataFile = open ("Courses.json", "w")
    dataFile.write(json.dumps(courses))
    dataFile.close()

    


class Users():
    def checkUser(ID):
        for users in usersData:
            if users["ID"] == ID:
                return users
        return False
    
    def registerUser(ID, name, studentID, number):
        tempUser = {"ID" : ID, "name" : name, "studentID" : studentID, "number" : str(number)}
        usersData.append(tempUser)
        saveLastData()
        





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    userID = update.message.from_user.id
    firstName = update.message.from_user.first_name

    ReplyKeyboardRemove()

    resultCheck = Users.checkUser(userID)
    if resultCheck:
        if userID in admins:
            buttons = [[KeyboardButton("📚 انتخاب واحد")],[KeyboardButton("📊 گزارش انتخاب دروس"), KeyboardButton("🧑‍🎓 لیست کاربران")],[KeyboardButton("📖 لیست دروس"), KeyboardButton("➕ افزودن درس")]]
            reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            await update.message.reply_text("منوی دسترسی:", reply_markup=reply)
        else:
            button = KeyboardButton("📚 انتخاب واحد")
            reply = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
            await update.message.reply_text(f"👋 سلام {resultCheck['name']} عزیز!\n🎯 لطفاً گزینه مورد نظر خود را از منوی زیر انتخاب کنید.", reply_markup=reply)
    else:
        await update.message.reply_text(f"👋 سلام {firstName} عزیز!\n🌟 برای ثبت‌نام، لطفاً نام خانوادگی خود را ارسال کنید:")
        context.user_data["level"] = 1

async def resiveMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userID = update.message.from_user.id
    firstName = update.message.from_user.first_name
    message = update.message.text
    if context.user_data.get("level"):
        if context.user_data["level"] == 1 :
            if message:
                context.user_data['name'] = message
                context.user_data["level"] = 2
                await update.message.reply_text("لطفاً کد دانشجویی خود را ارسال کنید.")
            else:
                await update.message.reply_text("Lotfan Name Khod Ra Vared Konid!")
        elif context.user_data["level"] == 2 :
            if len(message) == 9 and message.isdigit():
                context.user_data['studentId'] = message
                context.user_data["level"] = 3
                shareButton = KeyboardButton("Share Contact", request_contact=True)
                reply = ReplyKeyboardMarkup([[shareButton]], resize_keyboard=True)
                await update.message.reply_text("لطفاً شماره همراه خود را ارسال کنید.", reply_markup=reply)
            else:
                await update.message.reply_text("کد دانشجویی باید حتماً 9 رقم باشد. لطفاً مجدداً وارد کنید.") 
        elif context.user_data["level"] == 3 :
            contact = update.message.contact
            if contact:
                Users.registerUser(userID, context.user_data['name'], context.user_data['studentId'], contact.phone_number)
                
                button = KeyboardButton("📚 انتخاب واحد")
                reply = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
                await update.message.reply_text("سلام کاربر عزیز! لطفاً گزینه مورد نظر را انتخاب کنید.", reply_markup=reply) 
                context.user_data["level"] = 0
    elif context.user_data.get("add") :
        context.user_data["add"] = False
        courses[message] = []
        saveLastData()
        await update.message.reply_text(f"درس '{message}' با موفقیت اضافه شد.")
        
    else:
        if Users.checkUser(userID):
            if message == "📚 انتخاب واحد":
                message = "📚 دروس موجود برای انتخاب:\n\n"
                counter = 0
                keyboard = []
                for k,v in courses.items():
                    tempKeyboardMessage = ""
                    counter += 1
                    if userID in v:
                        message += ("✅ " + str(counter) + ". ")
                        tempKeyboardMessage += "✅ "
                    else:
                        message += ("❌ " + str(counter) + ". ")
                        tempKeyboardMessage += "❌ "
                    message += (k + "\n")
                    tempKeyboardMessage += k
                    keyboard.append([InlineKeyboardButton(tempKeyboardMessage, callback_data=k)])
                    
                        
           
                message += "\nبرای انتخاب یا حذف، روی دکمه‌های زیر کلیک کنید:"
                reply = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(message, reply_markup = reply)

            
            elif message == "📊 گزارش انتخاب دروس":
                message = "📊 گزارش انتخاب دروس:"
                for k,v in courses.items():
                    message += ("\n\n🔹 درس: " + k)
                    message += ("\n   📋 تعداد انتخاب‌ها: " + str(len(v)))
                    message += "\n  🧑‍🎓 انتخاب‌شده توسط:\n"
                    for i in v:
                        message += ("     🔸 " + Users.checkUser(i)["name"] + " (کد: " + Users.checkUser(i)["studentID"] + ")\n")

                await update.message.reply_text(message) 
            
            elif message == "🧑‍🎓 لیست کاربران":
                message = "🧑‍🎓 لیست کاربران:\n\n"
                counter = 0
                for i in usersData:
                    counter += 1
                    message += ("\n🔹 " + str(counter) + ". نام: " + i["name"] + " | " + " کد دانشجویی: " + i["studentID"] + " | " + " تلفن: " + i["number"])

                await update.message.reply_text(message) 
            
            elif message == "📖 لیست دروس":
                message = "📖 لیست دروس:\n"
                counter = 0
                for k,v in courses.items():
                    counter += 1
                    message += ("\n🔸 " + str(counter) + ". " + k)

                await update.message.reply_text(message) 

            elif message == "➕ افزودن درس":
                message = "لطفاً نام درس را وارد کنید:"
                context.user_data["add"] = True
                await update.message.reply_text(message)
                

async def courseSelection(update: Update, context: CallbackContext):
    userID = update.callback_query.from_user.id
    courseName = update.callback_query.data
    if userID in courses[courseName]:
        courses[courseName].remove(userID)
    else:
        courses[courseName].append(userID)

    saveLastData()

    message = "📚 دروس موجود برای انتخاب:\n\n"
    counter = 0
    keyboard = []
    for k,v in courses.items():
        tempKeyboardMessage = ""
        counter += 1
        if userID in v:
            message += ("✅ " + str(counter) + ". ")
            tempKeyboardMessage += "✅ "
        else:
            message += ("❌ " + str(counter) + ". ")
            tempKeyboardMessage += "❌ "
        message += (k + "\n")
        tempKeyboardMessage += k
        keyboard.append([InlineKeyboardButton(tempKeyboardMessage, callback_data=k)])


    message += "\nبرای انتخاب یا حذف، روی دکمه‌های زیر کلیک کنید:"
    reply = InlineKeyboardMarkup(keyboard)

    await update.callback_query.answer(f"درس {courseName} تغییر کرد.") 
    await update.callback_query.message.edit_text(message, reply_markup = reply)
    



application = ApplicationBuilder().token('TOKEN').build()


application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, resiveMessage))
application.add_handler(MessageHandler(filters.CONTACT, resiveMessage))
application.add_handler(CallbackQueryHandler(courseSelection))


application.run_polling()


