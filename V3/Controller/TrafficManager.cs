using Microsoft.AspNetCore.Mvc;
using Spectre.Console;

namespace V3
{
    [Route("Traffic/[controller]")]
    [ApiController]

    public class MapController : ControllerBase
    {
        [HttpGet("{id}")]
        public async Task<ActionResult<string>> PeekBoatRadar(int id, AppContext db)
        {
            const string Frame_top = "╔═════════════════════════════════════════════════════════════════════════════════════════════════════╗"; // == "╔" + new string('═', 100) + "╗";
            const string Frame_buttom = "\n╚═════════════════════════════════════════════════════════════════════════════════════════════════════╝"; // == "╚" + new string('═', 100) + "╝";
            const string Frame_side_left = "\n║"; // call left instead of right to initilize newline/row
            const string Frame_side_right = "║"; // call at end of row
            const int radarRange = 50;
            char[][] positions_zoomLVL200;

            // 1️⃣ Load current boat
            Coordinates currentBoat = db.Coordinates.SingleOrDefault(b => b.ID == id);
            if (currentBoat == null)
            {
                Console.WriteLine("Boat id not found. Exit Code 3");
                return "Boat id not found. Exit Code 3";
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
            string map = Frame_top + Frame_side_left;
            int i = 0;
            foreach (var row in positions_zoomLVL200)
            {
                // If you want Spectre.Console colors for different boats
                string line = string.Join("", row.Select(c => c switch
                {
                    'O' => "O", // current boat
                    'D' => "D",
                    'S' => "S",
                    _ => c.ToString()
                }));
                map += line + Frame_side_right;
                if(i == positions_zoomLVL200.Length - 1)
                {
                    map += Frame_buttom;
                    return map;
                }
                else
                {
                    map += Frame_side_left;
                    i++;
                } 
                AnsiConsole.MarkupLine(line);
            }
            return map;
        }
    }
}
