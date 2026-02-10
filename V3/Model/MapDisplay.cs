using System.ComponentModel.DataAnnotations;
using System.Security.Cryptography.X509Certificates;
using Spectre.Console;

public class MapDisplay
{
    // frame is currently 200 * 200 make sure 
    const string Frame_top = "╔════════════════════════════════════════════════════════════════════════════════════════════════════╗"; // == "╔" + new string('═', 100) + "╗";
    const string Frame_buttom = "\n╚════════════════════════════════════════════════════════════════════════════════════════════════════╝"; // == "╚" + new string('═', 100) + "╝";
    const string Frame_side_left = "\n║"; // call left instead of right to initilize newline/row
    const string Frame_side_right = "║"; // call at end of row
    // public char[,] positions_zoomLVL250 = null;
    // public char[,] positions_zoomLVL200 = null;
    // public char[,] positions_zoomLVL150 = null;
    // public char[,] positions_zoomLVL100 = null;
    // public char[,] positions_zoomLVL50 = null;
    public Coordinates coordinates;
    public MapDisplay()
    {
        coordinates = new Coordinates(Symbol_flag.Boat);
    }
    public void StartBoatSession(int id, AppContext db)
    {
        // 1️⃣ Load current boat
        var currentBoat = db.Coordinates.SingleOrDefault(b => b.ID == id);
        if (currentBoat == null)
        {
            Console.WriteLine("Boat id not found. Exit Code 3");
            return;
        }

        // 2️⃣ Load boats in radar range (exclude current boat)
        var boatsInRange = db.Coordinates
            .Where(b =>
                b.ID != currentBoat.ID &&
                Math.Abs(b.X - currentBoat.X) <= radarRange &&
                Math.Abs(b.Y - currentBoat.Y) <= radarRange)
            .ToList();

        // 3️⃣ Create jagged array
        int gridSize = radarRange * 2 + 1;
        positions_zoomLVL200 = new char[gridSize][];
        for (int y = 0; y < gridSize; y++)
        {
            positions_zoomLVL200[y] = new char[gridSize];
            for (int x = 0; x < gridSize; x++)
                positions_zoomLVL200[y][x] = ' '; // initialize blank
        }

        // 4️⃣ Set current boat in center
        int center = radarRange;
        positions_zoomLVL200[center][center] = 'O';

        // 5️⃣ Place other boats relative to current boat
        foreach (var boat in boatsInRange)
        {
            int dx = boat.X - currentBoat.X;
            int dy = boat.Y - currentBoat.Y;

            int arrayX = center + dx;
            int arrayY = center + dy;

            if (arrayX >= 0 && arrayX < gridSize && arrayY >= 0 && arrayY < gridSize)
                positions_zoomLVL200[arrayY][arrayX] = Symbol.GetSymbol(boat.Type);
        }

        // 6️⃣ Render radar
        RenderRadar();
    }
    private bool IsValidFrame()
    {
        bool isValid = true;
        if
        (
            Frame_top[0] != '╔'||
            Frame_top[Frame_top.Length - 1] != '╗'||
            Frame_buttom[0] != '╚'||
            Frame_buttom[Frame_buttom.Length - 1] != '╝'
        )
        {
            isValid = false;
            Console.WriteLine("Invalid frame corner");
            Console.WriteLine("Exit Code 1");
        }
        if (Frame_top.Length != Frame_buttom.Length)
        {
            isValid = false;
            Console.WriteLine("Top and buttom frame need equal length to be drawn");
            Console.WriteLine("Exit Code 2");
        }
        return isValid;
    }
    public void SimulateRadar()
    {
        bool isAlive = true;
        while(isAlive)
        {
            // List<Coordinates> filteredCoordinates = Coordinates.Entities.Where(x => x.)
            string line = Frame_side_left + new string(' ', Frame_top.Length - 2) + Frame_side_right;
        }
    }
    public void DisplayBlankMapExample()
    {
        string line = Frame_side_left + new string(' ', Frame_top.Length - 2) + Frame_side_right;
        string center_line = Frame_side_left + new string(' ', (Frame_top.Length - 2) / 2) + "[red bold]█[/]" + new string(' ', (Frame_top.Length - 3) / 2) + Frame_side_right;
        int drawCount = (Frame_top.Length - 2) / 2;
        int center = drawCount / 2;
        string map = "";
        while(drawCount != 0)
        {
            if(drawCount == center)
            {
                map += center_line;
            }
            else
            {
                map += line;
            }
            drawCount -= 1;
        }
        AnsiConsole.MarkupLine("[green bold]" + Frame_top + map + Frame_buttom + "[/]");
    }
    const int radarRange = 20; // radar shows ±20 units
    public char[][] positions_zoomLVL200;

    private void RenderRadar()
    {
        foreach (var row in positions_zoomLVL200)
        {
            // If you want Spectre.Console colors for different boats
            string line = string.Join("", row.Select(c => c switch
            {
                'O' => "[green]O[/]", // current boat
                'D' => "[yellow]D[/]",
                'S' => "[blue]S[/]",
                _ => c.ToString()
            }));
            AnsiConsole.MarkupLine(line);
        }
    }
}
