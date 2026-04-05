"""Game settings and constants."""

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Bob the Pirate"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
OCEAN_BLUE = (0, 105, 148)

# Player settings
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = -15
PLAYER_MAX_HEALTH = 5
GRAVITY = 0.8
MAX_FALL_SPEED = 15
INVINCIBILITY_FRAMES = 60  # 1 second at 60 FPS
KNOCKBACK_X = 8  # Horizontal knockback velocity
KNOCKBACK_Y = -6  # Vertical knockback velocity (negative = up)

# Attack settings
ATTACK_DURATION = 15  # frames
ATTACK_COOLDOWN = 20  # frames
ATTACK_RANGE = 24  # Matches the visual saber length
ATTACK_DAMAGE = 1
ATTACK_FRAME_WIDTH = 56  # Width of mid-swing attack frame

# Tile settings
TILE_SIZE = 32

# Enemy settings
SAILOR_SPEED = 2
SAILOR_HEALTH = 1
MUSKETEER_HEALTH = 2
MUSKETEER_SHOOT_COOLDOWN = 120  # 2 seconds
MUSKET_BALL_MAX_RANGE = 400  # Max distance musket ball travels before disappearing
OFFICER_SPEED = 3
OFFICER_HEALTH = 3
PROJECTILE_SPEED = 6

# Hawk settings
HAWK_HEALTH = 4
HAWK_FLY_SPEED = 3  # Horizontal patrol speed
HAWK_SWOOP_SPEED = 6  # Speed when diving at player
HAWK_DAMAGE = 2  # Talon attack damage
HAWK_DETECTION_RANGE = 200  # How close player must be to trigger swoop
HAWK_PATROL_RANGE = 150  # How far hawk flies from spawn point

# Collectibles
COIN_VALUE = 10
CHEST_POINTS = 100

# Power-ups
PARROT_DURATION = 600  # 10 seconds at 60 FPS
PARROT_ATTACK_COOLDOWN = 60
PARROT_DAMAGE = 1

# Cannon Shot power-up
CANNON_SHOT_AMMO = 8
CANNON_SHOT_DAMAGE = 2
CANNON_SHOT_SPEED = 10

# Double Jump power-up
DOUBLE_JUMP_DURATION = 1200  # 20 seconds at 60 FPS

# Cutlass Fury power-up
CUTLASS_FURY_DURATION = 600  # 10 seconds at 60 FPS
CUTLASS_FURY_COOLDOWN_MULT = 0.5  # Half cooldown
CUTLASS_FURY_RANGE_MULT = 1.5  # 50% wider hitbox

# Treasure Magnet power-up
MAGNET_DURATION = 1800  # 30 seconds (whole level basically)
MAGNET_RANGE = 150  # Pixels to pull from
MAGNET_STRENGTH = 5  # Speed of pull

# Monkey Mate power-up
MONKEY_DURATION = 720  # 12 seconds at 60 FPS
MONKEY_ATTACK_COOLDOWN = 45  # Faster than parrot
MONKEY_DAMAGE = 1
MONKEY_RANGE = 200  # Longer range than parrot
MONKEY_WIDTH = 20
MONKEY_HEIGHT = 16

# Miniboss settings (Bosun)
BOSUN_WIDTH = 44
BOSUN_HEIGHT = 64
BOSUN_HEALTH = 10
BOSUN_SPEED = 2
BOSUN_CHARGE_SPEED = 6
BOSUN_ATTACK_COOLDOWN = 30  # 0.5 seconds (was 0.75)
BOSUN_STOMP_DAMAGE = 2

# Boss settings
ADMIRAL_WIDTH = 48
ADMIRAL_HEIGHT = 72  # Taller than player (48) to be imposing
ADMIRAL_HEALTH = 15
ADMIRAL_SPEED = 2
ADMIRAL_PHASE_2_THRESHOLD = 9  # Phase 2 at 60% health
ADMIRAL_PHASE_3_THRESHOLD = 5  # Phase 3 at ~33% health
ADMIRAL_ATTACK_COOLDOWN = 60  # 1 second (was 1.5)
ADMIRAL_CHARGE_SPEED = 8
ADMIRAL_SUMMON_COOLDOWN = 240  # 4 seconds (was 5)
ADMIRAL_SWORD_FRAME_WIDTH = 70  # Width of mid-swing attack frame

# Ghost Captain settings (secret boss)
GHOST_CAPTAIN_WIDTH = 48
GHOST_CAPTAIN_HEIGHT = 72
GHOST_CAPTAIN_HEALTH = 18  # Very tough - hardest boss
GHOST_CAPTAIN_SPEED = 3
GHOST_CAPTAIN_ATTACK_COOLDOWN = 60  # 1 second
GHOST_CAPTAIN_TELEPORT_COOLDOWN = 120  # 2 seconds
GHOST_CAPTAIN_PHASE_DURATION = 45  # Invincible phase duration

# Ghost Captain skin settings (player skin, not the boss)
GHOST_SKIN_HEALTH_BONUS = 2  # +2 max health (7 total)
GHOST_SKIN_SPEED_MULT = 0.8  # 80% speed
GHOST_SKIN_ATTACK_DURATION = 120  # 2 seconds at 60 FPS (flame blast)
GHOST_SKIN_ATTACK_RANGE = 40  # Wider flame range
GHOST_SKIN_ATTACK_HEIGHT = 32  # Taller flame hitbox
GHOST_SKIN_CAN_MOVE_WHILE_ATTACKING = True  # Unique ability
GHOST_SKIN_ATTACK_FRAME_WIDTHS = [32, 56, 56]  # Sprite frame widths for flame attack

# Skeleton Pirate skin settings
SKELETON_SKIN_HEALTH_PENALTY = 2  # -2 max health (3 total)
SKELETON_SKIN_DAMAGE_MULT = 2.0  # 2x damage
SKELETON_SKIN_BONE_EVERY_N_ATTACKS = 4  # Throw bone every 4th attack
SKELETON_BONE_SPEED = 8  # Projectile speed
SKELETON_BONE_DAMAGE = 2  # Same as boosted melee
SKELETON_BONE_SIZE = 16  # Bone sprite size
SKELETON_BONE_RANGE = 300  # Max travel distance before despawning

# Parrot settings
PARROT_WIDTH = 16
PARROT_HEIGHT = 12

# Cannon settings
CANNON_SHOOT_COOLDOWN = 180  # 3 seconds
CANNONBALL_SPEED = 4.8
CANNONBALL_GRAVITY = 0.3

# Barrel Roll ability
BARREL_ROLL_SPEED = 12  # Faster than normal movement
BARREL_ROLL_DURATION = 15  # Frames (0.25 seconds)
BARREL_ROLL_COOLDOWN = 45  # Frames before can roll again
BARREL_ROLL_DOUBLE_TAP_WINDOW = 15  # Frames to detect double-tap

# Anchor Slam ability
ANCHOR_SLAM_SPEED = 20  # Fast downward velocity
ANCHOR_SLAM_DAMAGE = 2  # Damage dealt to enemies
ANCHOR_SLAM_RADIUS = 50  # Damage radius on landing
ANCHOR_SLAM_STUN_FRAMES = 30  # Stun duration for hit enemies
ANCHOR_SLAM_COOLDOWN = 60  # Frames before can slam again
ANCHOR_SLAM_FRAMES = 3  # Number of animation frames
