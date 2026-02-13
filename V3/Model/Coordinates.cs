public class Coordinates
{
    public int ID { get; set; }
    public float Y { get; set; }
    public float X { get; set; }
    public Symbol_flag Type;

    public Coordinates() { } // EF Core needs this
    public Coordinates(Symbol_flag type, float y = 0, float x = 0)
    {
        Type = type;
        Y = y;
        X = x;
        // Add this coordinate entity to list to display entity to other entities and ViseVersa.
        // Entities.Add(this);
    }
    private void Logic() => throw new NotImplementedException();
    public void Update_Y(float y) => Y += y;
    public void Update_X(float x) => X += x;
    public void Update(float x,  float y)
    {
        X += x;
        Y += y;
    }
}
    