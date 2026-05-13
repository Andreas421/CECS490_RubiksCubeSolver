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
    "white": [  #blue on top  
        ["white", "white", "white"],
        ["white", "white", "white"],
        ["orange", "orange", "orange"] 
    ],
    "yellow": [ #green on top
        ["red", "red", "red"],
        ["yellow", "yellow", "yellow"],
        ["yellow", "yellow", "yellow"]
         
    ]
}
'''

sample_captured_faces = {
    "blue": [ #white on top
        ["yellow", "green", "blue"],
        ["red", "blue", "blue"],
        ["orange", "red", "green"]
    ],
    "green": [ #white on top
        ["orange", "yellow", "red"],
        ["green", "green", "orange"],
        ["green", "orange", "orange"]
    ],
    "orange": [ #white on top
        ["orange", "red", "white"],
        ["orange", "orange", "white"],
        ["white", "blue", "yellow"]
    ],
    "red": [    #white on top
        ["blue", "blue", "red"],
        ["white", "red", "yellow"],
        ["green", "green", "blue"]
    ],
    "white": [  #green on top  
        ["white", "blue", "green"],
        ["white", "white", "green"],
        ["blue", "orange", "white"] 
    ],

    "yellow": [ #blue on top
        ["yellow", "white", "red"],
        ["yellow", "yellow", "red"],
        ["yellow", "yellow", "red"]
         
    ]
}

cube_string = reformat_cube_state(sample_captured_faces)

print("\n--- Full Cube String ---")
print(cube_string)

solution = solve_cube(cube_string)


print("\n--- Solve Instructions ---")
print(solution)