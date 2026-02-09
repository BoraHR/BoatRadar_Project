using System.ComponentModel.DataAnnotations;

public class MapDisplay
{
    // frame is currently 200 * 200 make sure 
    const string Frame_top = "╔════════════════════════════════════════════════════════════════════════════════════════════════════╗"; // = "╔" + new string('═', 100) + "╗";
    const string Frame_buttom = "\n╚════════════════════════════════════════════════════════════════════════════════════════════════════╝"; // = "╚" + new string('═', 100) + "╝";
    const string Frame_side_left = "\n║"; // used for both left and right
    const string Frame_side_right = "║";
    public Coordinates coordinates;
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
    public MapDisplay()
    {
        coordinates = new Coordinates(Symbol_flag.Boat);
    }
    public void DisplayBlankMapExample()
    {
        string line = Frame_side_left + new string(' ', Frame_top.Length - 2) + Frame_side_right;
        string center_line = Frame_side_left + new string(' ', (Frame_top.Length - 2) / 2) + "X" + new string(' ', (Frame_top.Length - 3) / 2) + Frame_side_right;
        int drawCount = (Frame_top.Length - 2) / 3;
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
        Console.WriteLine(Frame_top + map + Frame_buttom);
    }
}