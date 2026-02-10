using Microsoft.EntityFrameworkCore;

public class AppContext : DbContext
{
    public AppContext(DbContextOptions<AppContext> options) : base(options)
    {
    }

    // DbSet properties for your entities
    public DbSet<Coordinates> Coordinates { get; set; }
    public DbSet<MapDisplay> MapDisplays { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure Coordinates entity
        modelBuilder.Entity<Coordinates>(entity =>
        {
            entity.HasKey(e => e.ID);

            entity.Property(e => e.X)
                .IsRequired();

            entity.Property(e => e.Y)
                .IsRequired();

            entity.Property(e => e.Type)
                .IsRequired();
        });
    }
}
