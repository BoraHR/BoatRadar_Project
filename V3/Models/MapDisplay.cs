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
    public Coordinates coordinates;
    public MapDisplay()
    {
        coordinates = new Coordinates(Symbol_flag.Boat);
    }
    // start boat with the saved X - Y coordinates
    public void StartBoatSession(int id)
    {
        Coordinates coordinates = null;
        // Rework to read SQLdata.
        // while(true)
        // {
        //     foreach(var boat in Coordinates.Entities)
        //     {
        //         if(boat.ID == id)
        //         {
        //             coordinates = boat;
        //             break;
        //         }
        //     }
        //     break;
        // }
        if(coordinates == null)
        {
            Console.WriteLine("Boat id not found");
            Console.WriteLine("Exit Code 3");
            return;
        }
        while(true)
        {
            break;
        }
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
}