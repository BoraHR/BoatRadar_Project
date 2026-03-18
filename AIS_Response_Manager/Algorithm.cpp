#include <cmath>
#include <tuple>
#include <iostream>

double km_to_lat_deg(double km) {
    return km / 111.0;
}

double km_to_lon_deg(double km, double lat) {
    return km / (111.0 * std::cos(lat * M_PI / 180.0));
}

double bearing_deg(double lat1, double lon1, double lat2, double lon2) {
    // convert to radians
    lat1 = lat1 * M_PI / 180.0;
    lat2 = lat2 * M_PI / 180.0;
    double dLon = (lon2 - lon1) * M_PI / 180.0;

    double x = std::sin(dLon) * std::cos(lat2);
    double y = (std::cos(lat1) * std::sin(lat2) -
                std::sin(lat1) * std::cos(lat2) * std::cos(dLon));

    double bearing = std::atan2(x, y) * 180.0 / M_PI;

    // normalize to 0–360
    return std::fmod((bearing + 360.0), 360.0);
}

// haversine formula to find distance between two points on a sphere
double haversine(double lat1, double lon1, double lat2, double lon2) {
    double dLat = (lat2 - lat1) * M_PI / 180.0;
    double dLon = (lon2 - lon1) * M_PI / 180.0;

    lat1 = lat1 * M_PI / 180.0;
    lat2 = lat2 * M_PI / 180.0;

    double a = std::pow(std::sin(dLat / 2), 2) +
               std::pow(std::sin(dLon / 2), 2) * std::cos(lat1) * std::cos(lat2);
    double rad = 6371;
    double c = 2 * std::asin(std::sqrt(a));
    return rad * c;
}

std::tuple<double, double, double> ConvertToX_Y(double lat1, double lon1, double lat2, double lon2, bool debug = false) {
    double aardstraal = 6371000;
    double X1 = M_PI * lat1 / 180.0;
    double Y1 = M_PI * lon1 / 180.0;
    double X2 = M_PI * lat2 / 180.0;
    double Y2 = M_PI * lon2 / 180.0;
    double DeltaPhi = X1 - X2;
    double DeltaL = Y1 - Y2;
    double average = (X1 + X2) / 2.0;
    double Y = DeltaPhi * aardstraal;
    double X = DeltaL * aardstraal * std::cos(average);
    double distance = std::sqrt(X * X + Y * Y);
    if (debug) {
        std::cout << "X = " << X << "\n";
        std::cout << "Y = " << Y << "\n";
        std::cout << "Afstand = " << distance << "\n";
        std::cout << "return value: (" << X << ", " << Y << ", " << distance << ")\n";
    }
    return std::make_tuple(X, Y, distance);
}

std::pair<double, double> velocity_vector(double speed_knots, double heading_deg) {
    double speed_mps = speed_knots * 0.514444;  // knots → m/s
    double heading = heading_deg * M_PI / 180.0;

    double vx = speed_mps * std::sin(heading);
    double vy = speed_mps * std::cos(heading);

    return {vx, vy};
}

std::pair<double, double> calculate_cpa_tcpa(double x1, double y1, double speed1, double heading1,
                                             double x2, double y2, double speed2, double heading2) {
    auto [vx1, vy1] = velocity_vector(speed1, heading1);
    auto [vx2, vy2] = velocity_vector(speed2, heading2);

    double rx = x2 - x1;
    double ry = y2 - y1;

    double rvx = vx2 - vx1;
    double rvy = vy2 - vy1;

    double rv2 = rvx * rvx + rvy * rvy;

    if (rv2 == 0) {
        return {NAN, NAN};
    }

    double tcpa = -(rx * rvx + ry * rvy) / rv2;

    double cpa_x = rx + rvx * tcpa;
    double cpa_y = ry + rvy * tcpa;

    double cpa = std::sqrt(cpa_x * cpa_x + cpa_y * cpa_y);

    return {cpa, tcpa};
} 