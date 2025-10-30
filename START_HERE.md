# 🚗 Quick Start - Dealership Contact Automation

## Easiest Way: Double-Click to Launch

### **Just double-click this file:**
```
launch.command
```

That's it! The script will:
1. ✅ Install dependencies (first time only)
2. ✅ Start backend server
3. ✅ Start frontend server
4. ✅ Open browser automatically

**What you'll see:**
- Terminal window with status messages
- Browser opens to http://localhost:8000
- Green "Connected" indicator (bottom-right)

**To stop:**
- Press `Ctrl+C` in the terminal window
- Or just close the terminal

---

## Alternative: Use Terminal

If double-click doesn't work:

```bash
cd "/Users/iliasbeshimov/My Drive/Personal GDrive/Startup and Biz Projects/phrides.com car leasing help/Auto Contacting"
./launch.command
```

---

## What to Do in the UI

1. **Create a Search**
   - Click "Start New Search"
   - Enter your name, email, phone, zip code
   - Select vehicle make (Jeep, Ram, etc.)
   - Set search distance

2. **Select Dealerships**
   - Check boxes next to dealers you want to contact
   - Or click "All" to select everyone

3. **Start Contacting**
   - Click "Start Contacting" button
   - Watch real-time progress
   - See screenshots as they're captured

4. **Handle Special Cases**
   - **CAPTCHA detected?** Click "Fill Manually"
   - **Form not found?** Click website link to find it
   - **Success?** See confirmation screenshot!

---

## First Time Setup

The script handles everything automatically, but you need:

✅ **Python 3** - Already installed on your Mac
✅ **Internet connection** - To install dependencies
✅ **5-10 minutes** - First time setup

After first launch, it starts instantly next time!

---

## Troubleshooting

**Script won't run?**
```bash
chmod +x launch.command
./launch.command
```

**Port already in use?**
- Stop any other servers running on port 8000 or 8001
- Or restart your computer

**Backend fails to start?**
- Check `logs/backend.log` for errors
- Make sure Playwright is installed: `playwright install chromium`

**Need help?**
- Check `WEBSOCKET_README.md` for detailed guide
- Check `logs/backend.log` and `logs/frontend.log`

---

## That's It!

**Double-click `launch.command` and you're ready to go!** 🚀
