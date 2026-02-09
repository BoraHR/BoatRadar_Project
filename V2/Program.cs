using Spectre.Console;
using System.Timers;

Random rand = new Random();
var screen = new Canvas(80, 40);
var timer = new System.Timers.Timer(100);

int width = 80;
int height = 40;

// vessel positions
double x = 40, y = 20;
double vx = 0.5, vy = 0.2;

double x2 = 10, y2 = 10;
double vx2 = 0.3, vy2 = 0.4;

timer.Elapsed += (s, e) =>
{
    AnsiConsole.Clear();

    // update positions
    x += vx;
    y += vy;
    x2 += vx2;
    y2 += vy2;

    // bounce off walls
    if (x <= 0 || x >= width - 1) vx *= -1;
    if (y <= 0 || y >= height - 1) vy *= -1;

    if (x2 <= 0 || x2 >= width - 1) vx2 *= -1;
    if (y2 <= 0 || y2 >= height - 1) vy2 *= -1;

    // draw
    screen.SetPixel((int)x, (int)y, Color.Green);
    screen.SetPixel((int)x2, (int)y2, Color.Red);

    AnsiConsole.Clear();
    AnsiConsole.Write(screen);
};

timer.Start();
Console.ReadKey();
