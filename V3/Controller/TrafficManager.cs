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
            positions_zoomLVL200[center][center] = 'X';

            // 5️⃣ Place other boats relative to current boat
            foreach (var boat in boatsInRange)
            {
                float dx = boat.X - currentBoat.X;
                float dy = boat.Y - currentBoat.Y;

                float floatArrayX = center + dx;
                float floatArrayY = center + dy;

                int arrayX = (int)Math.Round(floatArrayX);
                int arrayY = (int)Math.Round(floatArrayY);

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
                    Console.WriteLine(map);
                    return map;
                }
                else
                {
                    map += Frame_side_left;
                    i++;
                }
            }
            return map;
        }
        [HttpPut("Drive/{id}/heading/{heading}/speed/{speed}/hold/{hold}")]
        public async Task<ActionResult<string>> DriveShip(int id, float heading, float speed, int hold, AppContext db)
        {
            var boat = db.Coordinates.SingleOrDefault(b => b.ID == id);

            if (boat == null)
                return NotFound("Boat not found");

            double radians = heading * Math.PI / 180.0;

            float deltaX = (float)(Math.Cos(radians) * speed);
            float deltaY = (float)(Math.Sin(radians) * speed);

            while (hold > 0)
            {
                Thread.Sleep(1000);

                boat.X += deltaX;
                boat.Y += deltaY;

                await db.SaveChangesAsync();

                Console.WriteLine($"Boat_{boat.ID} New position → X: {boat.X}, Y: {boat.Y}");
                hold--;
            }
            // 🔁 IMPORTANT: invert Y because array Y grows downward
            return Ok($"Boat_{boat.ID} New position → X: {boat.X}, Y: {boat.Y}");
        }
        [HttpGet("CalculateColision/B1_X/{B1_X}/B1_Y/{B1_Y}/B1_Heading/{B1_Heading}/B1_Speed/{B1_Speed}/B2_X/{B2_X}/B2_Y/{B2_Y}/B2_Heading/{B2_Heading}/B2_Speed/{B2_Speed}/Hold/{hold}")]
        public async Task<ActionResult<bool>> SimulateColisionCal(float B1_X, float B1_Y, float B1_Heading, float B1_Speed, float B2_X, float B2_Y, float B2_Heading, float B2_Speed, int hold)
        {
            double radians1 = B1_Heading * Math.PI / 180.0;
            double radians2 = B2_Heading * Math.PI / 180.0;

            float B1_deltaX = (float)(Math.Cos(radians1) * B1_Speed);
            float B1_deltaY = (float)(Math.Sin(radians1) * B1_Speed);

            float B2_deltaX = (float)(Math.Cos(radians2) * B2_Speed);
            float B2_deltaY = (float)(Math.Sin(radians2) * B2_Speed);

            while (hold > 0)
            {
                // Thread.Sleep(1000);

                B1_X += B1_deltaX;
                B1_Y += B1_deltaY;

                B2_X += B2_deltaX;
                B2_Y += B2_deltaY;
                
                Console.WriteLine($"Boat_1 New position → X: {B1_X}, Y: {B1_Y}");
                Console.WriteLine($"Boat_2 New position → X: {B2_X}, Y: {B2_Y}");


                if((int)Math.Round(B1_X) == (int)Math.Round(B2_X) && (int)Math.Round(B1_Y) == (int)Math.Round(B2_Y))
                {
                    Console.WriteLine("Boat_1 and Boat_2 got KIA'd");
                    return true;
                }
                hold--;
            }
            Console.WriteLine("Both boats survived");
            return false;
        }

    }
}
