using Microsoft.EntityFrameworkCore;

public class AppContext : DbContext
{
    public AppContext(DbContextOptions<AppContext> options) : base(options)
    {
    }

    // DbSet properties for your entities
    public DbSet<Coordinates> Coordinates { get; set; }
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure Coordinates entity
        modelBuilder.Entity<Coordinates>(entity =>
        {
            entity.HasKey(e => e.ID);

            entity.Property(e => e.ID)
                .ValueGeneratedOnAdd();

            entity.Property(e => e.X).IsRequired();
            entity.Property(e => e.Y).IsRequired();
            entity.Property(e => e.Type).IsRequired();
        });

        modelBuilder.Entity<Coordinates>().HasData(
            new Coordinates { ID = 1, Type = Symbol_flag.Boat, Y = 0, X = 0 },
            new Coordinates { ID = 2, Type = Symbol_flag.Boat, Y = 1, X = 10 },
            new Coordinates { ID = 3, Type = Symbol_flag.Boat, Y = 3, X = 20 },
            new Coordinates { ID = 4, Type = Symbol_flag.Boat, Y = -4, X = -14 },
            new Coordinates { ID = 5, Type = Symbol_flag.Boat, Y = -10, X = 26 },
            new Coordinates { ID = 6, Type = Symbol_flag.Boat, Y = 17, X = 30 },
            new Coordinates { ID = 7, Type = Symbol_flag.Boat, Y = 1000, X = 750 },
            new Coordinates { ID = 8, Type = Symbol_flag.Boat, Y = -38, X = 11 },
            new Coordinates { ID = 9, Type = Symbol_flag.Boat, Y = 1005, X = 735 },
            new Coordinates { ID = 10, Type = Symbol_flag.Boat, Y = 1010, X = 760 }
        );
    }
}
