public class Coordinates
{
    public static List<Coordinates> Entities = new();
    private static int _id;
    public int ID { get; }
    public int Y { get; set; }
    public int X { get; set; }
    public Symbol_flag Type;
    public Coordinates(Symbol_flag type, int y = 0, int x = 0)
    {
        // Fill fields.
        ID = _id;
        Type = type;
        Y = y;
        X = x;
        // Add this coordinate entity to list to display entity to other entities and ViseVersa.
        Entities.Add(this);
        // increament ID.
        _id += 1;
    }
    private void Logic() => throw new NotImplementedException();
    public void Update_Y(int y) => Y += y;
    public void Update_X(int x) => X += x;
    public void Update(int x, int y)
    {
        X += x;
        Y += y;
    }
}
    