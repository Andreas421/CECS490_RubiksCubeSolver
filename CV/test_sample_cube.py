from input_reformat import reformat_cube_state
from cube_solver import solve_cube

'''
#solved cube, apply F move & this is what should look like captured
sample_captured_faces = {
    "blue": [ #white on top
        ["blue", "blue", "blue"],
        ["blue", "blue", "blue"],
        ["blue", "blue", "blue"]
    ],
    "green": [ #white on top
        ["green", "green", "green"],
        ["green", "green", "green"],
        ["green", "green", "green"]
    ],
    "orange": [ #white on top
        ["orange", "orange", "yellow"],
        ["orange", "orange", "yellow"],
        ["orange", "orange", "yellow"]
    ],
    "red": [    #white on top
        ["white", "red", "red"],
        ["white", "red", "red"],
        ["white", "red", "red"]
    ],
    "white": [  #green on top 
        ["orange", "orange", "orange"], 
        ["white", "white", "white"],
        ["white", "white", "white"] 
    ],
    "yellow": [ #blue on top
        ["yellow", "yellow", "yellow"],
        ["yellow", "yellow", "yellow"],
        ["red", "red", "red"]  
    ]
}
'''

sample_captured_faces = {
    "blue": [ #white on top
        ["blue", "blue", "blue"],
        ["blue", "blue", "blue"],
        ["blue", "blue", "blue"]
    ],
    "green": [ #white on top
        ["green", "green", "green"],
        ["green", "green", "green"],
        ["green", "green", "green"]
    ],
    "orange": [ #white on top
        ["orange", "orange", "yellow"],
        ["orange", "orange", "yellow"],
        ["orange", "orange", "yellow"]
    ],
    "red": [    #white on top
        ["white", "red", "red"],
        ["white", "red", "red"],
        ["white", "red", "red"]
    ],
    "white": [  #green on top  
        ["white", "white", "white"],
        ["white", "white", "white"],
        ["orange", "orange", "orange"] 
    ],
    "yellow": [ #blue on top
        ["red", "red", "red"],
        ["yellow", "yellow", "yellow"],
        ["yellow", "yellow", "yellow"]
         
    ]
}

cube_string = reformat_cube_state(sample_captured_faces)

print("\n--- Full Cube String ---")
print(cube_string)

solution = solve_cube(cube_string)


print("\n--- Solve Instructions ---")
print(solution)