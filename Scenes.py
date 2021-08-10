import pygame
import random
import shutil
import os
from re import search


from Animations import Animation
from Sprites import Human
from Sprites import Bullet


def Menu(window, layersDict):
    
    GUISpriteGroup = pygame.sprite.Group()

    menuState = "True"
    while menuState == "True":
        # framerate
        clock = pygame.time.Clock()
        clock.tick(window.frameRate)

        # background
        window.screen.blit(window.bg, (0, 0))

        # for each reference to the layer in the layer dictionary...
        for layerRef in layersDict:
            layer = layersDict[layerRef]
            layer.Main()
            GUISpriteGroup.add(layer)
         
        # events (key presses, mouse presses)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuState = ""  # exits loop            

            # loops through all layers within the scene
            for layerRef in layersDict:
                layer = layersDict[layerRef]
                # checks if mouse clicks layers
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # condition for mouse click on layers
                    if layer.IsLayerClicked() == True:
                        # exits loop and returns the name of the layer clicked
                        GUISpriteGroup.empty()
                        menuState = layer.layerRender.originalText
        
        GUISpriteGroup.draw(window.screen)
        pygame.display.update()
        
    return menuState



def Game(window, layersDict, charList, humansDir):
    
    # INITIALISATIONS
    plyr = charList[0]
    enemy = charList[1]

    mouseVisibility = False
    limit_external_input = True

    is_dogfight_activated = False
    dogfight = False

    # HUMANS 
    # -------------------------------------------------------------------------------------------------------

    # converting it into an immutable and back to a list so program passes by value 
    humans = list(charList)
    humans.remove(plyr)
    humans.remove(enemy)    

    # instantiating all humans
    for character in charList:
        if character in humans:
            character.Main(window)

    # temp variable   
    # contains: man1, man2, girl1, girl2
    _humans = list(humans)

    no_of_instances = 0
    i = 0

    for _human in _humans:
           
        # counts how many times each human character appears within the humansDir folder 
        for dirs in os.listdir(humansDir):
            if search(_human.name, humansDir + dirs):
                no_of_instances += 1

        # if the number of characters are over what is intended
        # then remove the duplicates
        if no_of_instances > _human.max_no_of_instances:
            for _ in range(no_of_instances - _human.max_no_of_instances):
                shutil.rmtree(f"Images/people/{_human.name} - copy ({no_of_instances - _human.max_no_of_instances - 1})")
                no_of_instances -= 1

        # if the number of characters are under what is specified
        # add more copies of the folders
        elif no_of_instances < _human.max_no_of_instances:
            while i < _human.max_no_of_instances - no_of_instances:
                src = _human.anim.dir
                dest = _human.anim.dir + f" - copy ({i})"                
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                
                try:
                    shutil.copytree(src, dest)
                    i += 1
                except FileExistsError:
                    i += 1
                    dest = _human.anim.dir + f" - copy ({i})"

        # reset counters for next human character iteration
        i = 0
        no_of_instances = 0
 

    # generate Human Sprites off the copies that were generated above
    for directory in os.listdir(humansDir):
        randomNum = random.randint(1, 3) * 1000
        try:
            humanAnimCopy = [Animation(humansDir + directory, 100, -1)]
            humanCopy = Human(directory, 1/8, [3, 0], humanAnimCopy, window=window, health=1, walkTime=1000 + randomNum, waitTime=3000 + randomNum)
            humans.append(humanCopy)
        except NotADirectoryError:
            # some files are not folders, therefore exception
            pass
    

    # adding all the proper human characters to the characters list
    for human in humans:
        charList.append(human)


    # spreading all the humans equal distant apart from one another
    for i in range(len(humans)):
        equalSegments = window.width / len(humans)
        humans[i].rect.x = i * equalSegments

    # -------------------------------------------------------------------------------------------------------


    characterSpriteGroup = pygame.sprite.Group()
    characterSpriteGroup.add(character for character in charList)

    GUISpriteGroup = pygame.sprite.Group()

    
    # GAME MAIN LOOP
    # ----------------------------------------------------------------------------
    gameState = "Playing"
    while gameState == "Playing" or gameState == "Paused":


        # GAME FUNCTIONS 
        # ---------------------------------------------------------

        def InitAnim(char, anim):
            char.anim = anim
            # reset the cycles of the animation whenever it is called
            char.anim.currentCycles = 0
            char.anim.idx = 0

        

        def Pause(charList):
            for char in charList:
                char.anim.currentCycles = int(char.anim.maxCycles)
                char.is_moving = False
                if char in humans:
                    char.is_moving = False
                char.velocity = [0, 0]
            return "Paused"

        def Play(charList):
            for char in charList:
                char.anim.currentCycles = 0
                if char in humans:
                    char.is_moving = True
                char.velocity = list((char.speed))
            return "Playing"

        # ---------------------------------------------------------
        


        # MISCELLANEOUS
        # ---------------------------------------------------------

        # update layers within scene
        for layerRef in layersDict:
            layer = layersDict[layerRef]
            layer.Main()
            GUISpriteGroup.add(layer)


        # mouse visibility during the game
        pygame.mouse.set_visible(mouseVisibility)
        # limits all user input to pygame environment
        pygame.event.set_grab(limit_external_input)


        # if game is paused, do not get any input from player
        if gameState == "Playing":
            # getting state of all keys
            keys = pygame.key.get_pressed()

        # ---------------------------------------------------------


        # TIME
        # ---------------------------------------------------------

        # framerate
        clock = pygame.time.Clock()
        clock.tick(window.frameRate)
        # gets the time since start of Python in milliseconds
        curTime = pygame.time.get_ticks()        

        # ---------------------------------------------------------
        


        # PLAYER AND ENEMY
        # ------------------------------------------------------------------------------------------------------------------

        plyrColEnemy = plyr.rect.colliderect(enemy.rect)
        if plyrColEnemy and plyr.health > 0:
            InitAnim(plyr, plyr.animsDirList[1])
            InitAnim(enemy, enemy.animsDirList[1])
            plyr.health -= 1
            enemy.health -= 1

        # dogfight begins if B pressed, only for development reasons will be removed in final game.
        if keys[pygame.K_b]:
            is_dogfight_activated = True

        # ------------------------------------------------------------------------------------------------------------------



        # PLAYER
        # -----------------------------------------------------------------------------------------------

        # Animation

        # defaulting the player animation to idle, until another animaton is called
        #InitAnim(plyr, plyr.animsDirList[0])


        # Processing Player Input

        if gameState == "Playing":
            # keys[pygame.(any key)] is always either 0 (if not being pressed) or 1 (if being pressed); boolean value
            plyr_deltaVert = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            plyr_deltaHoriz = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        else:
            plyr_deltaVert = 0
            plyr_deltaHoriz = 0

        for event in pygame.event.get():
            # quitting the screen
            if event.type == pygame.QUIT:
                # exits loop
                gameState = "Quit"

            # if player hits escape, mouse is unhidden and player can move their input outside of the window;
            # if player hits mouse down, mouse is hidden and external input is once again hidden,
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mouseVisibility = True
                    limit_external_input = False

                # shoot bullet when space pressed
                if event.key == pygame.K_SPACE:
                    if (curTime - plyr.bullet.timeSinceLastCall >= plyr.bullet.cooldown):
                        plyr.bullet = Bullet(plyr.bulletImage, [20, 10], [
                                             10, 0], (plyr.rect.centerx, plyr.rect.bottom), 400, window)
                        plyr.bullet.InitVelocity(
                            plyr.velocity, plyr.flipSprite)
                        plyr.bullets.append(plyr.bullet)

                        plyr.bullet.timeSinceLastCall = curTime

                        # initialises the animation
                        InitAnim(plyr, plyr.animsDirList[2])

            if event.type == pygame.MOUSEBUTTONDOWN:
                if (mouseVisibility == True) and (limit_external_input == False) and (gameState != "Playing"):
                    mouseVisibility = False
                    limit_external_input = True
                for layerRef in layersDict:
                    layer = layersDict[layerRef]
                    # condition for mouse click on layers
                    if layer.IsLayerClicked() == True and gameState == "Playing":
                        # settings surface
                        window.layers.append(pygame.Surface((100, 200)))
                        # get the most recently added layer and fill it
                        window.layers[len(window.layers) -
                                      1].fill((100, 100, 100))
                        mouseVisibility = True
                        # pause the game
                        gameState = Pause(charList)

                    elif gameState == "Paused":
                        # resume the game
                        window.layers.pop(len(window.layers) - 1)
                        mouseVisibility = False
                        gameState = Play(charList)


        # Velocity

        # assigning the direction to the player's velocity
        # plyr_deltaHoriz and plyr_deltaVert are either 1, 0, -1, which assigns direction correctly        
        plyr.velocity[0] = plyr_deltaHoriz * plyr.speed[0]
        plyr.velocity[1] = plyr_deltaVert * plyr.speed[1]
        # diagonal velocity is to keep the player from travelling quicker 
        # than the normal horizontal and vertical speeds (pythagoras' theorem)
        # --> see Character class for more on diagonal velocity
        plyr.diagonalVelocity[0] = plyr_deltaHoriz * plyr.diagonalSpeed[0] 
        plyr.diagonalVelocity[1] = plyr_deltaVert * plyr.diagonalSpeed[1]
        # if player is going left, flip sprite
        plyr.flipSprite = keys[pygame.K_LEFT]

        # if the player is going diagonally, assign the diagonal speed
        if plyr_deltaHoriz != 0 and plyr_deltaVert != 0:
            plyr.velocity = plyr.diagonalVelocity


        # Restrictions

        if plyr.rect.x < 0:
            plyr.rect.x = 0
        elif plyr.rect.x + plyr.rect.width > window.width:
            plyr.rect.x = window.width - plyr.rect.width
        
        # if dogfight hasn't begun, then the upper boundaries are enemy location
        if dogfight == False and is_dogfight_activated == False:
            if plyr.rect.y < enemy.rect.height + enemy.rect.y + 10:
                plyr.rect.y = enemy.rect.height + enemy.rect.y + 10
        # else (if the dogfight has begun) then there are no upper boundaries
        else:
            if plyr.rect.y < 0:
                plyr.rect.y = 0
        # if the player is not dead, then the lower boundary is the human location
        if plyr.health > 0:
            if (plyr.rect.y + plyr.rect.height > 500 * (window.height / 720)):
                plyr.rect.y = 500 * (window.height / 720) - plyr.rect.height
        # else if the player has died, then they fall through the floor

        # add the velocity to the player's position
        plyr.rect.x += plyr.velocity[0]
        plyr.rect.y += plyr.velocity[1]


        # Bullets

        bulletColEnemy = False
        # updating all visible plyr bullets on screen
        for bullet in plyr.bullets:
            # deleting plyr bullets that travel off screen
            if bullet.rect.x + 5 < 0 or bullet.rect.x > window.width or bullet.rect.y < 0 or bullet.rect.y > window.height:
                plyr.bullets.remove(bullet)

            # updating bullet rect
            bullet.rect.x += bullet.velocity[0]
            bullet.rect.y += bullet.velocity[1]

            characterSpriteGroup.add(bullet)

            # if enemy gets hit
            bulletColEnemy = bullet.rect.colliderect(enemy.rect)
            if bulletColEnemy:
                plyr.bullets.remove(bullet)
                characterSpriteGroup.remove(bullet)
                InitAnim(enemy, enemy.animsDirList[1])
                enemy.health -= 1
                break


        # Player Death Condition
        if plyr.health == 0:
            InitAnim(plyr, plyr.animsDirList[3])

            for p_bullet in plyr.bullets:
                bullet.velocity[0] = 0
                characterSpriteGroup.remove(p_bullet)

            for e_bullet in enemy.bullets:
                characterSpriteGroup.remove(e_bullet)
            plyr.speed = [0, 0]
            plyr.diagonalSpeed = [0, 0]
            plyr.rect.y += 10
            

        # -----------------------------------------------------------------------------------------------



        # ENEMY
        # ----------------------------------------------------------------------------------------------------------------

        # enemy travelling to dogfight position
        if enemy.rect.x + enemy.rect.width < (window.width - 15) and is_dogfight_activated:
            enemy.rect.x += 8
        if enemy.rect.y < window.height/2 - enemy.rect.y/2 and is_dogfight_activated:
            enemy.rect.y += 8
        
        # if the enemy has reached the dogfight position..
        if enemy.rect.x + enemy.rect.width > (window.width - 16) and enemy.rect.y > (window.height/2 - enemy.rect.y/2 - 1) and is_dogfight_activated:
            enemy.flipSprite = True
            dogfight = True
            is_dogfight_activated = False
            print("Dogfight has been reached")

        # vertical and horizontal boundaries for enemy
        if enemy.rect.x < 0 or enemy.rect.x + enemy.rect.width > window.width:
            enemy.velocity[0] = -enemy.velocity[0]
        if enemy.rect.y < 0 or enemy.rect.y + enemy.rect.height > window.height:
            enemy.velocity[1] = -enemy.velocity[1]

        # if the game is in a state of playing (as opposed to paused)
        if gameState == "Playing":

            # if the enemy and player are in the dogfight session and the enemy is ready to shoot
            if (dogfight == True) and (curTime - enemy.bullet.timeSinceLastCall >= enemy.bullet.cooldown):
                enemy.bullet = Bullet(enemy.bulletImage, [20, 10], [10, 0], (enemy.rect.centerx, enemy.rect.bottom), 400, window)
                enemy.bullet.InitVelocity(enemy.velocity, enemy.flipSprite)
                enemy.bullets.append(enemy.bullet)
                InitAnim(enemy, enemy.animsDirList[2])

                enemy.bullet.timeSinceLastCall = curTime

            # if the enemy is not in a dogfight and its not going to be in a dogfight
            elif (dogfight == False) and (is_dogfight_activated == False):
                enemy.rect.x += enemy.velocity[0]

                if (curTime - enemy.bullet.timeSinceLastCall >= enemy.bullet.cooldown):
                    enemy.bullet = Bullet(enemy.bulletImage, [20, 10], [0, 10], (enemy.rect.centerx, enemy.rect.bottom), 400, window)
                    enemy.bullet.InitVelocity(enemy.velocity, enemy.flipSprite)
                    enemy.bullets.append(enemy.bullet)
                    InitAnim(enemy, enemy.animsDirList[0])

                    enemy.bullet.timeSinceLastCall = curTime

        
        # Bullets
     
        for bullet in enemy.bullets:
            # deleting enemy bullets that travel off screen
            if bullet.rect.x < 0 or bullet.rect.x > window.width or bullet.rect.y < 0 or bullet.rect.y > window.height:
                enemy.bullets.remove(bullet)

            # updating bullet rect
            bullet.rect.x += bullet.velocity[0]
            bullet.rect.y += bullet.velocity[1]

            characterSpriteGroup.add(bullet)

            bulletColPlyr = bullet.rect.colliderect(plyr.rect)
            if bulletColPlyr:
                enemy.bullets.remove(bullet)
                characterSpriteGroup.remove(bullet)
                InitAnim(plyr, plyr.animsDirList[1])
                plyr.health += -1
                print(plyr.health)


        # Enemy Health Bar

        r = min(255, 255 - (255 * ((2 * enemy.health - enemy.max_health) / enemy.max_health)))
        g = min(255, 255 * (enemy.health / (enemy.max_health / 2)))
        color = (r, g, 0)
        width = int(enemy.rect.width * enemy.health / enemy.max_health)
        enemy.health_bar = pygame.Rect(0, 0, width, 7)
        pygame.draw.rect(enemy.image, color, enemy.health_bar)



        # Enemy Death
        if enemy.health == 0:
            InitAnim(enemy, enemy.animsDirList[2])

            for p_bullet in plyr.bullets:
                p_bullet.velocity[0] = 0
                characterSpriteGroup.remove(p_bullet)

            for e_bullet in enemy.bullets:
                characterSpriteGroup.remove(e_bullet)

            plyr.speed = [0, 0]
            plyr.diagonalSpeed = [0, 0]
            enemy.rect.y -= 10


        # ------------------------------------------------------------------------------------------------------------------



        # HUMANS        
        # ---------------------------------------------------------------------------

        # human walking animation logic
        for human in humans:
            # boundary restrictions
            # if humans hit left border...
            if human.rect.x - 10 < 0:
                human.velocity[0] = abs(human.speed[0])
                human.flipSprite = False
            # if humans hit right border
            elif (human.rect.x + human.rect.width + 10) > window.width:
                human.velocity[0] = -human.speed[0]
                human.flipSprite = True
            
            # cooldown for stopping and is_dogfight_activated humans
            while ((pygame.time.get_ticks() - human.timeSinceLastCall) <= human.walkTime):
                human.anim.cooldown = human.anim.tempCooldown
                if human.flipSprite:
                    human.velocity = [-human.speed[0], 0]
                else:
                    human.velocity = [abs(human.speed[0]), 0]
                break
            else:
                if ((pygame.time.get_ticks() - human.timeSinceLastCall) >= (human.waitTime)):
                    human.timeSinceLastCall = pygame.time.get_ticks()
                
                human.velocity[0] = 0

        # ---------------------------------------------------------------------------


        # ALL CHARACTERS
        # -------------------------------------------------------------------------------------------------------

        # for every character present in the game
        for char in charList:
            if gameState == "Playing":
                # adding humans velocities
                if char in humans and char.is_moving:
                    char.rect.x += char.velocity[0]

                # Animation Logic:

                # if the cooldown for the animation has been reached
                if (curTime - char.anim.timeSinceLastCall >= char.anim.cooldown):
                    try:
                        # deactivate the animation if the maximum number of cycles has been reached
                        while char.anim.currentCycles != char.anim.maxCycles:

                            # update player rect
                            char.image = pygame.image.load(char.anim.framesList[char.anim.idx])
                            char.rect = char.image.get_rect(x=char.rect.x, y=char.rect.y)
                            char.rect.size = (int(char.rect.width * char.scaleFactor), int(char.rect.height * char.scaleFactor))

                            if char in humans:
                                if char.velocity[0] == 0:
                                    # setting the time for each frame to the time taken for humans to exit zero velocity,
                                    # essentially freezing the frame for the humans animation when they're still
                                    char.anim.cooldown = char.waitTime
                                elif char.velocity[0] < 0:
                                    char.flipSprite = True
                                elif char.velocity[0] > 0:
                                    char.flipSprite = False 
                            
                            # broadcast updated player info to the sprite's image component
                            char.image = pygame.transform.flip(
                                pygame.transform.scale(
                                        char.image,
                                    char.rect.size), 
                                char.flipSprite, False).convert_alpha()

                            char.anim.idx += 1
                            char.anim.currentCycles += 1
                            char.anim.timeSinceLastCall = curTime

                            break
                        else:
                            char.anim = char.animsDirList[0]
                            char.anim.idx = 0
                    except IndexError:
                        char.anim.idx = 0          

        # -------------------------------------------------------------------------------------------------------


        
        # DRAWING SURFACES
        # ------------------------------------------------------------------

        # drawing background
        window.screen.blit(window.bg, (0, 0))   


        # drawing all sprite groups 
        characterSpriteGroup.update()
        characterSpriteGroup.draw(window.screen)
        GUISpriteGroup.draw(window.screen)
        
        # drawing settings window
        for layers in window.layers:
            window.screen.blit(layers, (window.width/2, window.height/2, 100, 300))
        

        # updating screen
        pygame.display.update()

        # ------------------------------------------------------------------


    return

    # ----------------------------------------------------------------------------------------------
