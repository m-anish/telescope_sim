import pygame
import math
import tracker
import star_catalog

def spherical_to_cartesian(ra_deg, dec_deg):
    """
    Convert RA/Dec to Cartesian coordinates.
    This is a wrapper around the star_catalog function.
    """
    return star_catalog.ra_dec_to_cartesian(ra_deg, dec_deg)

def rotate_point(point, yaw, pitch):
    """
    Rotate a 3D point using the same logic as the camera.
    This applies the inverse camera transformation to world points.
    """
    # Apply yaw rotation (around Y-axis)
    vyaw = tracker.rotate_y(point, -math.radians(yaw))
    
    # Apply pitch rotation (around X-axis)
    vcam = tracker.rotate_x(vyaw, math.radians(pitch))
    
    return vcam

def project_point(point, fov_deg, width, height):
    """
    Project a 3D point to 2D screen coordinates.
    """
    x, y, z = point
    if z <= 0:  # Point is behind the camera
        return None
    
    # Calculate focal length
    fov_rad = math.radians(fov_deg)
    focal = (height / 2.0) / math.tan(fov_rad / 2.0)
    
    # Perspective projection
    sx = (width / 2.0) + (x * focal) / z
    sy = (height / 2.0) - (y * focal) / z  # Y is inverted in screen coordinates
    
    return (int(sx), int(sy))

def draw_stars_from_cartesian(screen, stars, camera, color=(255,255,255), show_names=False, font=None):
    """
    Draw stars from Cartesian coordinates using the camera system.
    
    Args:
        screen: Pygame screen surface
        stars: List of (x, y, z, magnitude, name) tuples
        camera: Camera object from tracker.py
        color: Base color for stars (brightness will be adjusted by magnitude)
        show_names: Boolean to toggle name display
        font: Pygame font object for text rendering
    """
    for x, y, z, mag, name in stars:
        # Transform to camera space
        vc = camera.world_to_camera((x, y, z))
        
        # Project to screen
        p = camera.project(vc)
        if not p:
            continue
            
        sx, sy, z_depth = p
        
        # Calculate brightness and size based on magnitude
        # Brighter stars (lower magnitude) appear bigger and brighter
        brightness = max(50, min(255, 255 - int(mag * 30)))
        size = max(1, min(4, 4 - int(mag / 2)))
        
        # Draw the star
        star_color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, star_color, (int(sx), int(sy)), size)
        
        # Draw name if enabled and conditions are met
        if show_names and mag < 2.0 and name and name.strip() and font:
            text_color = (200, 200, 200)  # Light gray for text
            text_surface = font.render(name, True, text_color)
            text_rect = text_surface.get_rect()
            # Position text to the right and slightly above the star
            text_rect.left = int(sx) + size + 3
            text_rect.centery = int(sy) - 2
            screen.blit(text_surface, text_rect)

def draw_constellations_from_cartesian(screen, constellations, camera, color=(100,100,255), show_names=False, font=None):
    """
    Draw constellation lines from Cartesian coordinates using the camera system.
    
    Args:
        screen: Pygame screen surface
        constellations: List of constellation dictionaries with Cartesian lines
        camera: Camera object from tracker.py
        color: Color for constellation lines
        show_names: Boolean to toggle name display
        font: Pygame font object for text rendering
    """
    for const in constellations:
        # Draw constellation lines
        for line in const["lines"]:
            if len(line) != 2:
                continue
                
            (x1, y1, z1), (x2, y2, z2) = line
            
            # Transform both points to camera space
            vc1 = camera.world_to_camera((x1, y1, z1))
            vc2 = camera.world_to_camera((x2, y2, z2))
            
            # Project both points to screen
            p1 = camera.project(vc1)
            p2 = camera.project(vc2)
            
            if p1 and p2:
                pygame.draw.line(screen, color, 
                               (int(p1[0]), int(p1[1])), 
                               (int(p2[0]), int(p2[1])), 1)
        
        # Draw constellation name if enabled and label exists
        if show_names and "label" in const and font:
            label_ra, label_dec = const["label"]
            
            # Convert label coordinates to Cartesian
            label_x, label_y, label_z = star_catalog.ra_dec_to_cartesian(label_ra, label_dec)
            
            # Transform to camera space and project to screen
            label_vc = camera.world_to_camera((label_x, label_y, label_z))
            label_p = camera.project(label_vc)
            
            if label_p:
                # Draw constellation name
                text_color = (150, 150, 255)  # Light blue for constellation names
                text_surface = font.render(const["name"], True, text_color)
                text_rect = text_surface.get_rect()
                # Position text centered at label position
                text_rect.center = (int(label_p[0]), int(label_p[1]))
                screen.blit(text_surface, text_rect)

def draw_messiers_from_cartesian(screen, messiers, camera, color=(255,180,80), show_names=False, font=None):
    """
    Draw Messier objects from Cartesian coordinates using the camera system.
    
    Args:
        screen: Pygame screen surface
        messiers: List of (m_num, name, x, y, z, magnitude, type, dim_major_deg, dim_minor_deg) tuples
        camera: Camera object from tracker.py
        color: Base color for Messier objects
        show_names: Boolean to toggle name display
        font: Pygame font object for text rendering
    """
    for m_num, name, x, y, z, mag, obj_type, dim_major, dim_minor in messiers:
        # Transform to camera space
        vc = camera.world_to_camera((x, y, z))
        
        # Project to screen
        p = camera.project(vc)
        if not p:
            continue
            
        sx, sy, z_depth = p
        
        # Check if we should draw an ellipse (product > 0.5 and dimensions are not null)
        if dim_major is not None and dim_minor is not None:
            product = dim_major * dim_minor
            if product > 0.5:
                # Convert angular dimensions to screen pixels
                # Scale based on camera FOV and screen dimensions
                width, height = screen.get_size()
                fov_rad = math.radians(camera.fov)
                focal_length = (height / 2.0) / math.tan(fov_rad / 2.0)
                
                # Convert angular size to linear size at the object's distance
                # Angular size in radians = size_in_radians = angular_size_deg * pi/180
                # Linear size = distance * tan(angular_size_in_radians)
                # Screen size = (linear_size * focal_length) / distance
                
                # For unit sphere objects, distance is approximately 1.0
                # So we can simplify: screen_size = focal_length * tan(angular_size_in_radians)
                major_angular_rad = math.radians(dim_major)
                minor_angular_rad = math.radians(dim_minor)
                
                # Calculate screen dimensions
                screen_major = int(focal_length * math.tan(major_angular_rad))
                screen_minor = int(focal_length * math.tan(minor_angular_rad))
                
                # Ensure minimum size for visibility
                screen_major = max(screen_major, 6)
                screen_minor = max(screen_minor, 6)
                
                # Draw ellipse
                ellipse_rect = pygame.Rect(
                    int(sx - screen_major/2),
                    int(sy - screen_minor/2),
                    screen_major,
                    screen_minor
                )
                pygame.draw.ellipse(screen, color, ellipse_rect)
                pygame.draw.ellipse(screen, (255,255,0), ellipse_rect, 1)
                
                # Draw name if enabled and conditions are met
                if show_names and mag < 5.0 and name and name.strip() and font:
                    text_color = (255, 200, 150)  # Light orange for messier text
                    text_surface = font.render(name, True, text_color)
                    text_rect = text_surface.get_rect()
                    # Position text below the ellipse
                    text_rect.centerx = int(sx)
                    text_rect.top = int(sy) + screen_minor//2 + 3
                    screen.blit(text_surface, text_rect)
                
                continue
        
        # Draw Messier object as a distinctive marker (fallback for small objects or null dimensions)
        pygame.draw.circle(screen, color, (int(sx), int(sy)), 3)
        pygame.draw.circle(screen, (255,255,0), (int(sx), int(sy)), 4, 1)
        
        # Draw name if enabled and conditions are met
        if show_names and mag < 5.0 and name and name.strip() and font:
            text_color = (255, 200, 150)  # Light orange for messier text
            text_surface = font.render(name, True, text_color)
            text_rect = text_surface.get_rect()
            # Position text below the circle marker
            text_rect.centerx = int(sx)
            text_rect.top = int(sy) + 6
            screen.blit(text_surface, text_rect)

# Legacy functions for backward compatibility
def draw_stars(screen, stars, yaw, pitch, fov, color=(255,255,255)):
    """Legacy function - use draw_stars_from_cartesian instead."""
    width, height = screen.get_size()
    for ra, dec, mag in stars:
        p = spherical_to_cartesian(ra, dec)
        p = rotate_point(p, yaw, pitch)
        proj = project_point(p, fov, width, height)
        if proj:
            brightness = max(0, 255 - int(mag * 40))
            size = max(1, 3 - int(mag / 2))
            pygame.draw.circle(screen, (brightness, brightness, brightness), proj, size)

def draw_constellations(screen, constellations, yaw, pitch, fov, color=(100,100,255)):
    """Legacy function - use draw_constellations_from_cartesian instead."""
    width, height = screen.get_size()
    for const in constellations:
        for (ra1, dec1), (ra2, dec2) in const["lines"]:
            p1 = spherical_to_cartesian(ra1, dec1)
            p2 = spherical_to_cartesian(ra2, dec2)
            p1r = rotate_point(p1, yaw, pitch)
            p2r = rotate_point(p2, yaw, pitch)
            proj1 = project_point(p1r, fov, width, height)
            proj2 = project_point(p2r, fov, width, height)
            if proj1 and proj2:
                pygame.draw.line(screen, color, proj1, proj2, 1)
