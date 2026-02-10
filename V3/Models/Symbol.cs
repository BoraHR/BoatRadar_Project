public enum Symbol_flag
{
    Dock,
    Boat,
    Submarine,
    Other
}

public static class Symbol
{
    public static char GetSymbol(Symbol_flag sym)
    {
        char Mark = 'E';
        switch (sym)
        {
            case Symbol_flag.Boat:
                Mark = 'O';
                break;
            
            case Symbol_flag.Dock:
                Mark = 'D';
                break;

            case Symbol_flag.Submarine:
                Mark = 'S';
                break;

            case Symbol_flag.Other:
                Mark = 'E';
                break;
        }
        return Mark;
    }
}