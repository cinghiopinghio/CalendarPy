import locale
import yaml
import calendar
from PIL import Image  # pip install pillow
from PIL import ImageDraw
from PIL import ImageFont

with open('config.yaml', 'rt') as fin:
    config = yaml.load(fin)

# get the right locale for days and moth names
if config.get('locale', '') == '':
    lcl = locale.getlocale()
else:
    lcl = config['locale']
locale.setlocale(locale.LC_ALL, locale=lcl)
DAYS = [
    locale.DAY_1,
    locale.DAY_2,
    locale.DAY_3,
    locale.DAY_4,
    locale.DAY_5,
    locale.DAY_6,
    locale.DAY_7,
]
DAYS = [locale.nl_langinfo(d).capitalize() for d in DAYS]

MONTHS = [
    locale.MON_1,
    locale.MON_2,
    locale.MON_4,
    locale.MON_4,
    locale.MON_5,
    locale.MON_6,
    locale.MON_7,
    locale.MON_8,
    locale.MON_9,
    locale.MON_10,
    locale.MON_11,
    locale.MON_12,
]
MONTHS = [locale.nl_langinfo(m) for m in MONTHS]

# first week day
# 0: Monday; 6: Sunday
FWD = config.get('first_week_day', 6)

# the year
YEAR = int(config.get('year', 1917))

FONTS = {
    'font': config.get('font', 'arial.ttf'),
    'mono': config.get('font-mono', 'cour.ttf')
}


def DayText(Day):
    if FWD == 0:
        Day = (Day + 1) % 7
    return DAYS[Day]


def MonthText(Month):
    return MONTHS[Month-1]


def MaxFont(draw, text, rect, mono=False):
    Font = FONTS['font']
    if mono:
        Font = FONTS['mono']
    fsize = 1
    font = ImageFont.truetype(Font, fsize)
    while (draw.textsize(text, font)[0] < (rect[2]-rect[0]) and
           draw.textsize(text, font)[1] < (rect[3]-rect[1])):
        fsize += 1
        font = ImageFont.truetype(Font, fsize)
    return font


def GetCentered(draw, text, font, rect):
    W = rect[2]-rect[0]
    H = rect[3]-rect[1]
    w, h = draw.textsize(text, font)
    return (rect[0]+(W-w)//2, rect[1]+(H-h)//2)


# Make rectangle one pixel smaller
def Shrink(rectangle):
    return (rectangle[0]+1, rectangle[1]+1,
            rectangle[2]-1, rectangle[3]-1)


# Draw thinker boardered rectangle
def DrawRectangle(draw, rectangle, width=1, fill='white'):
    for i in range(width):
        draw.rectangle(rectangle, outline=(0, 0, 0), fill=fill)
        rectangle = Shrink(rectangle)


def Calendar(year, month):
    dpi = 300
    Width = int(11.7 * dpi)
    Height = int(8.3 * dpi)
    Margin = int(.5 * dpi)

    cal = Image.new("RGB", (Width, Height), "white")
    draw = ImageDraw.Draw(cal)

    Header = Height//5
    HeaderCellWidth = (Width-2*Margin)//7
    HeaderCellHeight = (Height-2*Margin)//20

    # Draw samll previous month
    PrevSmallCalendarRect = (2*Margin,
                             Margin,
                             2*Margin + Header + Margin - HeaderCellHeight,
                             Header + Margin - HeaderCellHeight)
    smallPrevBegin = PrevSmallCalendarRect[:2]

    if month == 1:
        smallPrev = calendar.TextCalendar(FWD
                                          ).formatmonth(year-1, 12)
    else:
        smallPrev = calendar.TextCalendar(FWD
                                          ).formatmonth(year, month-1)
    font = MaxFont(draw, smallPrev, PrevSmallCalendarRect, True)
    draw.text(smallPrevBegin, smallPrev, (0, 0, 0), font=font)

    # Draw small next month
    NextSmallCalendarRect = [x for x in PrevSmallCalendarRect]
    NextSmallCalendarRect[0] = Width - 2*Margin - (PrevSmallCalendarRect[2] -
                                                   PrevSmallCalendarRect[0])
    NextSmallCalendarRect[2] = Width - 2*Margin
    smallNextBegin = NextSmallCalendarRect[:2]

    if month == 12:
        smallNext = calendar.TextCalendar(FWD).formatmonth(year+1, 1)
    else:
        smallNext = calendar.TextCalendar(FWD).formatmonth(year, month+1)
    font = MaxFont(draw, smallNext, NextSmallCalendarRect, True)
    draw.text(smallNextBegin, smallNext, (0, 0, 0), font=font)

    # Draw day labels
    Padding = int(HeaderCellWidth*.05)
    DaysLabelRect = (Margin + HeaderCellWidth * 3+Padding,
                     Header + Margin - HeaderCellHeight + Padding,
                     Margin + 4*HeaderCellWidth - Padding,
                     Header + Margin - Padding)
    font = MaxFont(draw, DayText(3), DaysLabelRect)

    for Day in range(7):
        DaysLabelRect = (Margin + HeaderCellWidth * Day,
                         Header + Margin - HeaderCellHeight,
                         Margin + HeaderCellWidth * (Day+1),
                         Header + Margin)
        DaysTextLabelRect = [DaysLabelRect[0]+Padding,
                             DaysLabelRect[1]+Padding,
                             DaysLabelRect[2]-Padding,
                             DaysLabelRect[3]-Padding]

        DrawRectangle(draw, DaysLabelRect, 3)
        draw.text(GetCentered(draw, DayText(Day),
                              font, DaysTextLabelRect),
                  DayText(Day), (0, 0, 0), font=font)

    Days = calendar.Calendar(FWD).monthdayscalendar(year, month)

    Weeks = len(Days)
    CellWidth = (Width - 2 * Margin) // 7
    CellHeight = (Height - 2 * Margin-Header) // Weeks
    Padding = int(CellWidth*.05)
    for week in range(Weeks):
        for Day in range(7):
            DaysRect = (Margin + CellWidth * Day,
                        Header + Margin + CellHeight * week,
                        Margin + CellWidth * Day + CellWidth,
                        Header + Margin + CellHeight * week + CellHeight)
            fill = 'white'
            if Day == 6 or (FWD == 0 and Day == 5) or\
               (FWD == 6 and Day == 0):
                fill = '#cccccc'
            DrawRectangle(draw, DaysRect, 3, fill=fill)
            DaysTextRect = [x+Padding for x in DaysRect]

            if Days[week][Day] > 0:
                draw.text(DaysTextRect, str(Days[week][Day]), (0, 0, 0),
                          font=font)

    # Draw Header
    Padding = int(Width*.05)
    HeaderText = "{} {}".format(MonthText(month).capitalize(), year)
    HeaderRect = (PrevSmallCalendarRect[2]+Padding,
                  PrevSmallCalendarRect[1],
                  NextSmallCalendarRect[0]-Padding,
                  NextSmallCalendarRect[3])

    font = MaxFont(draw, HeaderText, HeaderRect)
    draw.text(GetCentered(draw, HeaderText, font, HeaderRect),
              HeaderText, (0, 0, 0), font=font)

    cal.save('{}-{:02d}.pdf'.format(year, month))


if __name__ == "__main__":
    for m in range(12):
        Calendar(YEAR, m+1)
